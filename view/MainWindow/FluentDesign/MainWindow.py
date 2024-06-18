# coding:utf-8
import sys
from pathlib import PurePath

from PyQt6.QtCore import QTimer, QEventLoop, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import SplashScreen, FluentWindow

from util.config import IMG_PATH
from view.MainWindow.MacOS.MainWindow import MainWindow
from qfluentwidgets import FluentIcon as FIF

ICON = str(IMG_PATH.joinpath(PurePath('star_of_life.png')))


class Demo(FluentWindow):

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


        self.main_window = MainWindow()
        self.main_window.setObjectName('MainWindow')
        self.addSubInterface(self.main_window, FIF.HOME, 'Home')
        self.navigationInterface.hide()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(ICON))
    w = Demo()
    w.show()
    w.showMaximized()
    app.exec()
