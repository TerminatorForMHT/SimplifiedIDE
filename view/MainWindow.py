# coding:utf-8
import sys
from pathlib import PurePath

from PyQt6.QtCore import QTimer, QEventLoop, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import SplashScreen

from util.config import IMG_PATH
from view.UserInterface import UserInterface
from view.WindowBase import WindowBase

ICON = str(IMG_PATH.joinpath(PurePath('snake.svg')))


class MainWindow(WindowBase):

    def __init__(self):
        super().__init__()
        self.resize(700, 600)
        self.setWindowTitle('PythonPad++')
        self.setWindowIcon(QIcon(ICON))

        # 1. 创建启动页面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        # 2. 在创建其他子页面前先显示主界面
        self.show()

        # 3. 创建子界面
        self.createSubInterface()

        # 4. 隐藏启动页面
        self.splashScreen.finish()

        self.user_interface = UserInterface(self)
        self.user_interface.setObjectName('UserInterface')
        self.addSubInterface(self.user_interface)

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON))
    w = MainWindow()
    w.show()
    w.showMaximized()
    app.exec()
