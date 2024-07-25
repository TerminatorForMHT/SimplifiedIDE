import logging
from pathlib import PurePath

import autopep8
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtCore import QFile, QTextStream, Qt, pyqtSignal, QEvent, QStringConverter
from PyQt6.QtGui import QColor, QShortcut, QKeySequence, QFont, QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from qfluentwidgets import SmoothScrollDelegate, FluentStyleSheet, setFont

from conf.config import IMG_PATH, SEP, MySettings
from util.code_check import run_pylint_on_code
from util.jediLib import JdeiLib
from util.lexer import LEXER_MAP


class Editor(QsciScintilla):
    """
    Python代码编辑器实现类
    """
    ctrl_left_click_signal = pyqtSignal(dict)

    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.zoom_level = 0
        self.setStyleSheet('margin: 2px;')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollDelegate = SmoothScrollDelegate(self)

        self.current_file_path = None
        self.file_name = None
        self.syntax_errors = []
        self.init_actions()

        self.setMouseTracking(True)
        self.viewport().installEventFilter(self)
        self.underlined_word_range = None

        FluentStyleSheet.LINE_EDIT.apply(self)
        setFont(self)

    def init_ui(self, lexer):
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        self.setMarginsFont(font)

        self.setLexer(lexer)

        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)
        self.setTabIndents(True)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setFoldMarginColors(QColor("#fafafa"), QColor("#fafafa"))
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        self.setIndentationGuides(True)
        self.setMarginType(1, QsciScintilla.MarginType.NumberMargin)
        self.setMarginsBackgroundColor(QColor("#FFFFFF"))
        self.setMarginsForegroundColor(Qt.GlobalColor.gray)
        self.setMarginSensitivity(1, True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setPaper(QColor("#ffffff"))
        self.setColor(QColor("#000000"))

        self.setMarginLineNumbers(0, True)
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
        self.setCaretLineBackgroundColor(QColor("#e0e0e0"))
        self.setCaretForegroundColor(QColor("#0078d7"))
        self.SendScintilla(QsciScintilla.SCI_SETSELBACK, True, QColor("#d6ebff"))

        self.INDICATOR_ERROR = 0
        self.INDICATOR_WARN = 1
        self.UNDERLINED_WORD = 2
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_ERROR, QsciScintilla.INDIC_SQUIGGLE)
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_WARN, QsciScintilla.INDIC_SQUIGGLE)
        self.SendScintilla(QsciScintilla.SCI_INDICSETUNDER, self.UNDERLINED_WORD, QsciScintilla.INDIC_STRAIGHTBOX)
        self.installEventFilter(self)

        self.markerDefine(QsciScintilla.MarkerSymbol.Minus, QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.markerDefine(QsciScintilla.MarkerSymbol.Plus, QsciScintilla.SC_MARKNUM_FOLDER)

        self.setMarkerBackgroundColor(QColor("#0078D7"), QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerForegroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDER)
        self.setMarkerBackgroundColor(QColor("#0078D7"), QsciScintilla.SC_MARKNUM_FOLDEROPEN)
        self.setMarkerForegroundColor(QColor("#FFFFFF"), QsciScintilla.SC_MARKNUM_FOLDEROPEN)

    def init_actions(self):
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Alt+L"), self).activated.connect(self.reformat)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.comment_selected)
        self.wheelEvent = self.handle_wheel_event

    def load_file(self, file_path):
        self.current_file_path = file_path
        file_suffix = file_path.split('.')[-1]
        lexer = LEXER_MAP.get(f".{file_suffix}", QsciLexerPython)
        try:
            self.init_ui(lexer())
        except Exception as e:
            self.init_ui(lexer)
            logging.error(e)
        self.file_name = file_path.split(SEP)[-1].rstrip(".py")
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            stream.setEncoding(QStringConverter.Encoding.Utf8)
            self.setText(stream.readAll())
            file.close()

    def save_file(self):
        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as file:
                file.write(self.text())
        except Exception as e:
            logging.warning(e)
        finally:
            return

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if Qt.KeyboardModifier.ControlModifier:
            if event.modifiers():
                pos = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, int(event.position().x()),
                                         int(event.position().y()))
                line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, pos) + 1
                index = self.SendScintilla(QsciScintilla.SCI_GETCOLUMN, pos)
                jedi_lib = JdeiLib(source=self.text(), filename=self.current_file_path)
                jump_info = {
                    "assign_addr": jedi_lib.getAssignment(line, index),
                    "reference_addr": jedi_lib.getReferences(line, index),
                }
                self.ctrl_left_click_signal.emit(jump_info)

    def move_cursor_visible(self, line, index=0):
        if line:
            self.setCursorPosition(line - 1, index)
            self.ensureLineVisible(line + self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN) // 2)

    def handle_wheel_event(self, event):
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
                self.add_wavy_underline(error.get('line'), error.get('column'), error.get('endLine'),
                                        error.get('endColumn'), 'E' not in error.get('message-id') and
                                        'F' not in error.get('message-id'))

    def get_cursor_pos(self):
        cursor_pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        cursor_line = self.SendScintilla(self.SCI_LINEFROMPOSITION, cursor_pos)
        cursor_index = cursor_pos - self.SendScintilla(self.SCI_POSITIONFROMLINE, cursor_line)
        return cursor_index, cursor_line

    def contextMenuEvent(self, event):
        # 获取默认的右键菜单
        menu = self.createStandardContextMenu()

        if self.current_file_path.endswith('.py'):
            # 添加自定义的操作项
            run_icon = str(IMG_PATH.joinpath(PurePath('play_green.svg')))
            self.code_run_action = QAction(QIcon(run_icon), f"Run {self.file_name}", self)
            self.code_run_action.triggered.connect(self.code_run)
            menu.addAction(self.code_run_action)

        # 显示菜单
        menu.exec(event.globalPos())

    def code_run(self):
        env = MySettings.value("default_interpreter")
        if env:
            print(f'{env} {self.current_file_path}')
        else:
            QMessageBox.warning(self, "执行错误", "请选择基础解释器！")

    def eventFilter(self, obj, event):
        if obj is self.viewport() and event.type() == QEvent.Type.MouseMove:
            pos = event.pos()
            self.handleMouseHover(pos)
            return True
        elif obj is self.viewport() and event.type() == QEvent.Type.Leave:
            self.clearUnderline()
            return True
        return super(Editor, self).eventFilter(obj, event)

    def handleMouseHover(self, pos):
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            pos_in_doc = self.positionFromPoint(pos)
            if pos_in_doc == -1:
                self.clearUnderline()
                return

            word_start, word_end = self.getWordBoundary(pos_in_doc)
            if word_start != -1 and word_end != -1:
                self.clearUnderline()
                self.underlineWord(word_start, word_end)
                self.underlined_word_range = (word_start, word_end)
        else:
            self.clearUnderline()

    def positionFromPoint(self, pos):
        # 将像素位置转换为文本位置
        return self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, pos.x(), pos.y())

    def getWordBoundary(self, pos):
        # 获取指定位置的单词边界
        start = self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, pos, True)
        end = self.SendScintilla(QsciScintilla.SCI_WORDENDPOSITION, pos, True)
        return start, end

    def underlineWord(self, start, end):
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, self.UNDERLINED_WORD, QColor('blue'))
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start, end - start)

    def clearUnderline(self):
        if self.underlined_word_range:
            start, end = self.underlined_word_range
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, start, end - start)
            self.underlined_word_range = None
