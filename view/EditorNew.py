import logging

from PyQt6.Qsci import QsciScintilla, QsciAPIs, QsciLexerPython
from PyQt6.QtCore import pyqtSignal, Qt, QFile, QTextStream, QStringConverter, QEvent
from PyQt6.QtGui import QFont, QColor

from conf.config import SEP
from util.jediLib import JdeiLib
from util.lexer import LEXER_MAP


class Editor(QsciScintilla):
    """
    Python代码编辑器实现类
    """
    ctrl_left_click_signal = pyqtSignal(dict)
    code_execut_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._parent = parent

        self.init_ui()
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
        self.setAutoCompletionThreshold(1)  # 输入1个字符后触发补全

        # 连接文本变化信号，动态更新补全列表
        self.textChanged.connect(self.update_completion)

    def init_ui(self):
        """
        初始化UI
        """
        # 设置字体
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        self.setMarginsFont(font)

        # 设置缩进
        self.setAutoIndent(True)
        self.setTabIndents(True)
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)

        # 设置代码折叠样式为 BoxedTreeFoldStyle
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        # 设置折叠边距的背景颜色
        self.setFoldMarginColors(QColor("#fafafa"), QColor("#fafafa"))
        # 设置第 2 个边距为符号边距
        self.setMarginType(2, QsciScintilla.MarginType.SymbolMargin)
        # 启用缩进参考线
        self.setIndentationGuides(True)
        # 设置第 1 个边距为行号边距
        self.setMarginType(1, QsciScintilla.MarginType.NumberMargin)
        # 设置边距背景颜色为白色
        self.setMarginsBackgroundColor(QColor("#FFFFFF"))
        # 设置边距前景颜色为灰色
        self.setMarginsForegroundColor(Qt.GlobalColor.gray)
        # 设置第 1 个边距对点击事件敏感
        self.setMarginSensitivity(1, True)
        # 设置括号匹配模式为 SloppyBraceMatch
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        # 设置编辑器背景颜色为白色
        self.setPaper(QColor("#ffffff"))
        # 设置编辑器文本颜色为黑色
        self.setColor(QColor("#000000"))

        # 启用第 0 个边距的行号显示
        self.setMarginLineNumbers(0, True)
        # 设置第 1 个边距的宽度为 4 个字符宽度
        self.setMarginWidth(1, "0000")
        # 设置边缘模式为 EdgeLine
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        # 设置边缘列位置为 80 列
        self.setEdgeColumn(80)
        # 设置边缘线颜色为浅灰色
        self.setEdgeColor(QColor("#bebebe"))
        # 启用当前行高亮
        self.setCaretLineVisible(True)
        # 设置当前行背景颜色为浅灰色
        self.setCaretLineBackgroundColor(QColor("#e0e0e0"))
        # 设置光标颜色为蓝色
        self.setCaretForegroundColor(QColor("#0078d7"))
        # 设置选中文本的背景颜色为浅蓝色
        self.SendScintilla(QsciScintilla.SCI_SETSELBACK, True, QColor("#d6ebff"))

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

    def update_completion(self):
        """当文本变化时，使用 Jedi 获取补全建议并更新 QsciAPIs"""
        # 获取当前文本
        line, index = self.get_cursor_pos()

        # 使用 Jedi 获取补全建议
        jedi_lib = JdeiLib(source=self.text(), filename=self.current_file_path)
        completions = jedi_lib.getCompletions(line, index)

        # 创建 QsciAPIs 对象并添加补全词
        self.apis = QsciAPIs(self.lexer)
        for completion in completions:
            self.apis.add(completion.name)
        self.apis.prepare()

        # 更新编辑器的补全列表
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)