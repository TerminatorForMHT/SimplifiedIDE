import logging
from pathlib import PurePath

import autopep8
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtCore import QFile, QTextStream, Qt, pyqtSignal, QEvent, QStringConverter, QPoint, QTimer
from PyQt6.QtGui import QColor, QShortcut, QKeySequence, QFont, QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QListWidgetItem, QListWidget, QAbstractItemView
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
    completion_text_signal = pyqtSignal(list)

    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.zoom_level = 0
        self.completion_list_widget = QListWidget(self)
        self.completion_list_widget.setWindowFlags(Qt.WindowType.ToolTip)
        self.completion_list_widget.hide()
        # 禁用垂直滚动条
        self.completion_list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 禁用水平滚动条
        self.completion_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cursor_pos = None

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
        self.textChanged.connect(self.show_completion)

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
        self.textChanged.disconnect(self.show_completion)
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
        QTimer.singleShot(0, lambda: self.textChanged.connect(self.show_completion))

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
        # 获取当前光标的位置
        cursor_position = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        # 获取行号
        line, _ = self.lineIndexFromPosition(cursor_position)
        # 获取该行的起始位置
        line_start_position = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
        # 计算列号（当前光标位置 - 行起始位置）
        column = cursor_position - line_start_position
        return line + 1, column + 1

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

    def get_word_before_cursor(self):
        # 获取光标的当前位置
        current_pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)

        # 获取光标前一个单词的开始位置
        word_start_pos = self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, current_pos, True)

        # 如果光标位置和单词开始位置不相同
        if word_start_pos < current_pos:
            return self.text()[word_start_pos:current_pos]
        return ""

    def show_completion(self):
        cursor_word = self.get_word_before_cursor()
        if cursor_word == "":
            return

        # 获取Jedi补全
        jedi_lib = JdeiLib(source=self.text(), filename=self.current_file_path)
        line, index = self.get_cursor_pos()
        completion_list = jedi_lib.getCompletions(line, index)

        if completion_list:
            self.completion_list_widget.clear()
            for item in completion_list:
                self.completion_list_widget.addItem(item)

            # 获取当前光标位置的坐标
            cursor_position = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            cursor_x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, cursor_position)
            cursor_y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, cursor_position)

            # 将文档内坐标转换为屏幕坐标
            global_cursor_pos = self.mapToGlobal(QPoint(cursor_x, cursor_y))

            # 显示补全列表在光标下方
            self.completion_list_widget.setGeometry(global_cursor_pos.x(),
                                                    global_cursor_pos.y() + self.textHeight(line), 300, 100)
            self.completion_list_widget.show()
            self.completion_list_widget.setCurrentRow(0)
        else:
            self.completion_list_widget.hide()

    def point_from_position(self, cursor_pos):
        x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, cursor_pos[0], cursor_pos[1])
        y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, cursor_pos[0], cursor_pos[1])
        return x, y

    def complete_text(self, item):
        if item:
            text = item.text()
            self.insertCompletion(text)
            self.completion_list_widget.hide()

    def insertCompletion(self, text):
        # 获取当前光标的位置
        line, index = self.getCursorPosition()

        # 获取当前光标位置
        cursor_position = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        # 获取当前光标前单词的起始位置
        word_start_position = self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, cursor_position, True)
        # 计算单词的长度
        word_length = cursor_position - word_start_position
        # 删除光标前的单词
        self.SendScintilla(QsciScintilla.SCI_DELETERANGE, word_start_position, word_length)

        # 插入补全的文本
        self.insert(text)

        # 更新光标位置
        self.setCursorPosition(line, index + len(text))

    def keyPressEvent(self, event):
        if self.completion_list_widget.isVisible():
            if event.key() == Qt.Key.Key_Tab or event.key() == Qt.Key.Key_Return:
                current_item = self.completion_list_widget.currentItem()
                if current_item:
                    self.complete_text(current_item)
                return
            elif event.key() == Qt.Key.Key_Up:
                current_row = self.completion_list_widget.currentRow()
                self.completion_list_widget.setCurrentRow(max(current_row - 1, 0))
                return
            elif event.key() == Qt.Key.Key_Down:
                current_row = self.completion_list_widget.currentRow()
                self.completion_list_widget.setCurrentRow(min(current_row + 1, self.completion_list_widget.count() - 1))
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.completion_list_widget.hide()
                return

        super(Editor, self).keyPressEvent(event)
