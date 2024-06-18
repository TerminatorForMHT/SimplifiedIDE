import platform
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    icon = QIcon('src/static/img/snake.svg')
    app = QApplication(sys.argv)
    app.setWindowIcon(icon)
    if platform.system() == 'Darwin':
        from view.MainWindow.MacOS.MainWindow import MainWindow
    elif platform.system() == 'Windows':
        from view.MainWindow.Windows.MainWindow import MainWindow
    window = MainWindow()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())
