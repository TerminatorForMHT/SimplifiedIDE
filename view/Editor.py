import logging

import autopep8
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtCore import QFile, QTextStream, Qt, pyqtSignal, QStringConverter
from PyQt6.QtGui import QColor, QShortcut, QKeySequence, QFont

from util.code_check import run_pylint_on_code

from util.jediLib import JdeiLib


class Editor(QsciScintilla):
    """
    Python代码编辑器实现类
    """
    ctrl_left_click_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_file_path = None
        self.syntax_errors = []
        self.init_ui()
        self.init_actions()

    def init_ui(self):
        lexer = QsciLexerPython()
        self.setLexer(lexer)

        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)
        self.setTabIndents(True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setIndentationGuides(True)
        self.setMarginType(1, QsciScintilla.MarginType.NumberMargin)
        self.setMarginsFont(QFont("Courier", 10))
        self.setMarginsBackgroundColor(QColor("#cccccc"))
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, "0000")
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusExplicit)
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor("#bebebe"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#e4e4e4"))

        self.INDICATOR_ERROR = 0
        self.INDICATOR_WARN = 1
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_ERROR, QsciScintilla.INDIC_SQUIGGLE)
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_WARN, QsciScintilla.INDIC_SQUIGGLE)
        self.installEventFilter(self)

    def init_actions(self):
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Alt+L"), self).activated.connect(self.reformat)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.comment_selected)
        self.wheelEvent = self.handle_wheel_event

    def load_file(self, file_path):
        self.current_file_path = file_path
        self.setReadOnly("pyi" in file_path)
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            try:
                stream.setEncoding(QStringConverter.Encoding.System)
                self.setText(stream.readAll())
            except UnicodeDecodeError:
                stream.setEncoding(QStringConverter.Encoding.Utf8)
                self.setText(stream.readAll())
            file.close()

    def save_file(self):
        with open(self.current_file_path, 'w') as file:
            file.write(self.text())

    def mousePressEvent(self, event):
        if Qt.KeyboardModifier.ControlModifier and event.modifiers():
            pos = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, int(event.position().x()),
                                     int(event.position().y()))
            line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, pos) + 1
            index = self.SendScintilla(QsciScintilla.SCI_GETCOLUMN, pos)
            jedi_lib = JdeiLib(source=self.text(), filename=self.current_file_path)
            jump_info = {
                "assign_addr": jedi_lib.getAssignment(line, index),
                "reference_addr": jedi_lib.getReferences(line, index)
            }
            self.ctrl_left_click_signal.emit(jump_info)
        super().mousePressEvent(event)

    def move_cursor_visible(self, line, index=0):
        if line:
            self.setCursorPosition(line - 1, index)
            self.ensureLineVisible(line + self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN) // 2)

    def handle_wheel_event(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoomIn() if event.angleDelta().y() > 0 else self.zoomOut()
            event.accept()
        else:
            QsciScintilla.wheelEvent(self, event)

    def reformat(self):
        self.setText(autopep8.fix_code(self.text()))

    def comment_selected(self):
        if self.selectedText():
            lines = self.selectedText().split('\n')
            commented = [f"# {line}" if not line.startswith("#") else line[2:] for line in lines]
            self.replaceSelectedText('\n'.join(commented))
        else:
            line, _ = self.getCursorPosition()
            ori_text = self.text(line)
            new_text = f"# {ori_text}" if not ori_text.startswith("#") else ori_text[2:]
            self.setSelection(line, 0, line, len(ori_text))
            self.replaceSelectedText(new_text)

    def add_wavy_underline(self, start_line, start_index, end_line, end_index, is_warn):
        color = '#ffcc00' if is_warn else 'red'
        indicator_type = self.INDICATOR_WARN if is_warn else self.INDICATOR_ERROR
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, indicator_type, QColor(color))
        start_pos = self.positionFromLineIndex(start_line - 1, start_index)
        end_pos = self.positionFromLineIndex((end_line or start_line) - 1, end_index or start_index + 1)
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_type)
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_pos, end_pos - start_pos)

    def check_code(self):
        if self.text():
            try:
                self.save_file()
            except Exception as e:
                logging.error(e)
            self.syntax_errors = run_pylint_on_code(self.current_file_path)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE)
            for error in self.syntax_errors:
                if error.get('type') == 'convention':
                    continue
                self.add_wavy_underline(error.get('line'), error.get('column'), error.get('endLine'),
                                        error.get('endColumn'),
                                        'E' not in error.get('message-id') and 'F' not in error.get('message-id'))

    def get_cursor_pos(self):
        cursor_pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        cursor_line = self.SendScintilla(self.SCI_LINEFROMPOSITION, cursor_pos)
        cursor_index = cursor_pos - self.SendScintilla(self.SCI_POSITIONFROMLINE, cursor_line)
        return cursor_index, cursor_line
