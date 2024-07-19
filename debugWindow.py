import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow

from demo import PackageManagement
from view.EnvManageBox import EnvManageBox


class MainWindow(QMainWindow):
    def __init__(self, debug_widget):
        super().__init__()
        self.debug_widget = debug_widget()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Debug Window")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.debug_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow(EnvManageBox)
    mainWin.show()
    sys.exit(app.exec())
