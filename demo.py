import sys
from PyQt6.QtWidgets import QMainWindow, QApplication

from view.Editor import Editor


class JediQsciEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 QScintilla 编辑器
        self.editor = Editor(self)
        self.setCentralWidget(self.editor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JediQsciEditor()
    window.editor.load_file(__file__)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())