from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.Qsci import QsciScintilla, QsciLexerPython

class CustomLexerPython(QsciLexerPython):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCustomColors()

    def setCustomColors(self):
        # Example colors, replace with actual PyCharm light theme colors
        self.setColor(QColor("#000000"), QsciLexerPython.Default)       # Default text
        self.setColor(QColor("#0000FF"), QsciLexerPython.Keyword)       # Keywords
        self.setColor(QColor("#008000"), QsciLexerPython.Comment)       # Comments
        self.setColor(QColor("#800080"), QsciLexerPython.Number)        # Numbers
        self.setColor(QColor("#FF0000"), QsciLexerPython.DoubleQuotedString)  # Double quoted strings
        self.setColor(QColor("#FF0000"), QsciLexerPython.SingleQuotedString)  # Single quoted strings
        self.setColor(QColor("#800080"), QsciLexerPython.FunctionMethodName)  # Function names
        self.setColor(QColor("#808000"), QsciLexerPython.Operator)      # Operators
        self.setColor(QColor("#008080"), QsciLexerPython.Identifier)    # Identifiers
        self.setColor(QColor("#800000"), QsciLexerPython.CommentBlock)  # Block comments
        self.setColor(QColor("#008080"), QsciLexerPython.ClassName)     # Class names
        self.setColor(QColor("#800080"), QsciLexerPython.Decorator)     # Decorators

    def styleText(self, start, end):
        super().styleText(start, end)
        self.highlightSelfKeywords(start, end)

    def highlightSelfKeywords(self, start, end):
        editor = self.editor()
        text = editor.text()
        pos = text.find("self", start)
        while pos != -1 and pos < end:
            if self.isSelfKeyword(text, pos):
                editor.SendScintilla(editor.SCI_STARTSTYLING, pos)
                editor.SendScintilla(editor.SCI_SETSTYLING, len("self"), 8)  # Use a custom style number
            pos = text.find("self", pos + 1)

    def isSelfKeyword(self, text, pos):
        if pos > 0 and text[pos-1].isalnum():
            return False
        if pos + len("self") < len(text) and text[pos + len("self")].isalnum():
            return False
        return True