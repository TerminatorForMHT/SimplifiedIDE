import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from view.MainWindow import ICON, MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('PythonPad++')
    app.setApplicationVersion('0.0.1')
    app.setWindowIcon(QIcon(ICON))
    w = MainWindow()
    w.show()
    w.showMaximized()
    app.exec()
