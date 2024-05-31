import autopep8
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.QtCore import QFile, QTextStream, Qt, pyqtSignal
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

        self.jump_info = None
        self.syntax_errors = None
        self.current_file_path = None

        self.init_ui()
        self.init_actions()

    def init_ui(self):
        lexer = QsciLexerPython()
        self.setLexer(lexer)

        # 代码缩进
        self.setAutoIndent(True)
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)

        # 代码块折叠
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)  # 设置折叠样式，具体样式可能因版本而异
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)

        # 启用显示垂直缩进指南线
        self.setIndentationGuides(True)

        self.setMarginType(1, QsciScintilla.MarginType.NumberMargin)  # 设置行号区域的宽度，可以根据需要调整
        self.setMarginsFont(QFont("Courier", 10))
        self.setMarginsBackgroundColor(QColor("#cccccc"))
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, "0000")

        # 代码补全提示
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)  # 设置自动补全源
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)  # 补全时不区分大小写
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusExplicit)

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor("#bebebe"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#e4e4e4"))
        self.installEventFilter(self)

        self.INDICATOR_ERROR = 0
        self.INDICATOR_WARN = 1
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_ERROR, QsciScintilla.INDIC_SQUIGGLE)
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, self.INDICATOR_WARN, QsciScintilla.INDIC_SQUIGGLE)

        self.installEventFilter(self)

    def init_actions(self):
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)

        shortcut_format = QShortcut(QKeySequence("Ctrl+Alt+L"), self)
        shortcut_format.activated.connect(self.reformat)

        # 添加快捷键Ctrl+/用于注释代码
        shortcut_comment = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        shortcut_comment.activated.connect(self.comment_selected)

        self.wheelEvent = self.handleWheelEvent

        self.selected_text = self.selectedText()

    def load_file(self, file_path):
        # 设置当前文件路径，以便保存时使用
        self.current_file_path = file_path
        if "pyi" in file_path:
            self.setReadOnly(True)
        file = QFile(file_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            self.setText(stream.readAll())
            file.close()

    def save_file(self):
        with open(self.current_file_path, 'w') as file:
            file.write(self.text())

    def mousePressEvent(self, event):
        __jump_info = {}
        jediLib = JdeiLib(source=self.text(), filename=self.current_file_path)
        if Qt.KeyboardModifier.ControlModifier and event.modifiers():
            line, index = self.getCursorPosition()
            line += 1
            assign_addr = jediLib.getAssignment(line, index)
            reference_addr = jediLib.getReferences(line, index)
            if assign_addr:
                __jump_info["assign_addr"] = assign_addr
            if reference_addr:
                __jump_info["reference_addr"] = reference_addr
            self.ctrl_left_click_signal.emit(__jump_info)
        del jediLib
        super().mousePressEvent(event)

    def move_cursor_visible(self, line, index=0):
        """
        将光标移动到指定的行和列，并确保该位置可见。

        :param line: 目标行号
        :param index: 目标列索引，默认为行首
        """
        if line:
            # 确保光标位置大致居中
            len_screen = self.SendScintilla(QsciScintilla.SCI_LINESONSCREEN)
            line_offset = len_screen // 2
            if line % len_screen > line_offset:
                self.ensureLineVisible(line + line_offset)
            else:
                self.ensureLineVisible(line)
            # 移动光标到指定位置
            self.setCursorPosition(line - 1, index)
        else:
            return

    def handleWheelEvent(self, event):
        # 检查Ctrl键是否被按下
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # 根据滚轮方向执行放大或缩小
            if event.angleDelta().y() > 0:
                self.zoomIn()  # 向上滚动放大
            else:
                self.zoomOut()  # 向下滚动缩小
            # 阻止事件传播，避免默认的滚动行为
            event.accept()
        else:
            # 如果没有按Ctrl键，则按照默认处理方式
            QsciScintilla.wheelEvent(self, event)

    def reformat(self):
        origin_code = self.text()
        formatted_code = autopep8.fix_code(origin_code)
        self.setText(formatted_code)

    def comment_selected(self):
        temp_list = []
        if self.selectedText():
            for line in self.selectedText().split('\n'):
                words = line.split()
                if "#" != words[0]:
                    if len(words) >= 1:
                        temp_list.append(line.replace(words[0], f'# {words[0]}'))
                else:
                    temp_list.append(line.replace('# ', '', 1))
            self.replaceSelectedText('\n'.join(temp_list))
        return

    def add_wavy_underline(self, start_line, start_index, end_line, end_index, info_type):
        """
        在指定的行列范围添加波浪线标记
        """
        # 获取开始和结束位置的索引
        end_line = end_line if end_line else start_line
        end_index = end_index if end_index else start_index + 1

        start_pos = self.positionFromLineIndex(start_line - 1, start_index)
        end_pos = self.positionFromLineIndex(end_line - 1, end_index)

        # 设置标记颜色
        color = '#ffcc00' if info_type else 'red'
        indicator_type = self.INDICATOR_WARN if info_type else self.INDICATOR_ERROR
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE, indicator_type, QColor(color))

        # 设置标记范围
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, indicator_type)
        self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_pos, end_pos - start_pos)

    def check_code(self):
        if self.text() is not None:
            self.save_file()
            errors = run_pylint_on_code(self.current_file_path)
            self.syntax_errors = errors
            for error in errors:
                is_warn = True
                self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE)
                start_line, start_index = error.get('line'), error.get('column')
                end_line, end_index = error.get('endLine'), error.get('endColumn')
                if error.get('type') == 'convention':
                    continue
                elif 'E' in error.get('message-id') or 'F' in error.get('message-id'):
                    is_warn = False
                self.add_wavy_underline(start_line, start_index, end_line, end_index, is_warn)

    def get_cursor_pos(self):
        cursor_pos = self.SendScintilla(self.SCI_GETCURRENTPOS)
        cursor_line = self.SendScintilla(self.SCI_LINEFROMPOSITION, cursor_pos)
        cursor_index = (cursor_pos - self.SendScintilla(self.SCI_POSITIONFROMLINE, cursor_line) +
                        len(self.selected_text))
        return cursor_index, cursor_line
