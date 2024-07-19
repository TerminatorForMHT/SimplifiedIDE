import json
import logging
import os
import sys
from pathlib import PurePath

from PyQt6.QtCore import Qt, QEventLoop, QTimer, QSize
from PyQt6.QtGui import QColor, QPainter, QIcon
from PyQt6.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QSplitter, QListWidget, QPushButton, QSizePolicy, QMenu,
                             QMessageBox)
from qfluentwidgets import qconfig, isDarkTheme, SplashScreen, FluentTitleBar
from qfluentwidgets.common.animation import BackgroundAnimationWidget
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from qframelesswindow import TitleBar

from conf.config import IMG_PATH, ROOT_PATH, MySettings
from ui.style_sheet import ButtonStyleSheet

from view.CreateVenvMessageBox import CreateVenvMessageBox
from view.DockWidget import DockWidget
from view.UserInterface import UserInterface

ICON = str(IMG_PATH.joinpath(PurePath('snake.svg')))


class MainWindow(BackgroundAnimationWidget, FramelessWindow):
    def __init__(self, parent=None):
        self.env_file = ROOT_PATH / 'conf' / "env_history.json"
        self.env_history = self.load_env_history()
        self._isMicaEnabled = False
        self._lightBackgroundColor = QColor(243, 243, 243)
        self._darkBackgroundColor = QColor(32, 32, 32)
        super().__init__(parent)
        self.setup_titlebar()
        self.setup_start_window()
        self.setup_window()
        self.setup_layout()
        self.setup_ui_elements()
        self.setStyleSheet('background-color: rgba(255, 255, 255, 0)')
        self.show()
        last_env = MySettings.value("default_interpreter")
        last_env_name = MySettings.value("default_interpreter_name")
        if last_env and last_env_name:
            env_info = {
                'name': last_env_name,
                'path': last_env
            }
            self.set_default_interpreter(env_info)

    def setup_titlebar(self):
        self.setTitleBar(FluentTitleBar(self))
        self.setWindowTitle('PythonPad++')
        self.setWindowIcon(QIcon(ICON))

    def setup_start_window(self):

        self.resize(700, 600)
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.titleBar.hide()
        self.splashScreen.setIconSize(QSize(102, 102))
        self.show()
        self.createSubInterface()
        self.splashScreen.finish()

    def setup_window(self):
        self.syntax_error = None
        self.setMicaEffectEnabled(True)
        qconfig.themeChangedFinished.connect(self._onThemeChangedFinished)

    def setup_layout(self):
        self.hBoxLayout = QHBoxLayout(self)
        self.mainWidget = QWidget(self)
        self.widgetLayout = QVBoxLayout(self.mainWidget)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.mainWidget)
        self.widgetLayout.setContentsMargins(0, 30, 0, 0)
        self.widgetLayout.addWidget(self.mainWidget)
        self.setLayout(self.hBoxLayout)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.user_interface = UserInterface()
        self.user_interface.open_file_signal.connect(self.resetChangeTimer)
        self.dock_widget = DockWidget(self)
        self.dock_widget.hide_signal.connect(self.hide_dock)
        self.splitter.addWidget(self.user_interface)
        self.splitter.addWidget(self.dock_widget)
        self.splitter.setSizes([int(self.width() * 0.9), int(self.width() * 0.1)])
        self.widgetLayout.addWidget(self.splitter)
        self.titleBar.raise_()
        self.dock_widget.hide()

    def setup_ui_elements(self):
        self.button_widget = QWidget()
        self.button_widget.setLayout(QHBoxLayout())
        self.button_widget.setFixedHeight(40)
        self.toggleButton = self.create_status_button('syntax_info.svg', self.switch_widget, 0)
        self.show_log_button = self.create_status_button('play.svg', self.switch_widget, 1)
        self.button_widget.layout().addWidget(self.toggleButton)
        self.button_widget.layout().addWidget(self.show_log_button)
        python_exec_icon = QIcon(str(IMG_PATH.joinpath(PurePath('python_env.svg'))))
        self.dock_btn = QPushButton("", self)
        self.dock_btn.setIcon(python_exec_icon)
        self.dock_btn.setCheckable(True)
        self.dock_btn.setChecked(True)
        self.dock_btn.setStyleSheet(ButtonStyleSheet)
        self.dock_btn.clicked.connect(self.show_dock_menu)
        self.button_widget.layout().addWidget(self.dock_btn)
        self.button_widget.layout().setSpacing(0)
        self.button_widget.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.button_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.widgetLayout.addWidget(self.button_widget)
        self.__changeTimer = QTimer()
        self.__changeTimer.timeout.connect(self.check_syntax)
        self.__changeTimer.start(5000)
        self.__changeTimer.stop()

    def create_status_button(self, icon_path, callback, index):
        button = QPushButton("", self)
        button.setCheckable(True)
        button.setChecked(True)
        button.setIcon(QIcon(str(IMG_PATH.joinpath(PurePath(icon_path)))))
        button.setStyleSheet(ButtonStyleSheet)
        button.clicked.connect(lambda: callback(index))
        return button

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()

    def setCustomBackgroundColor(self, light, dark):
        self._lightBackgroundColor = QColor(light)
        self._darkBackgroundColor = QColor(dark)
        self._updateBackgroundColor()

    def _normalBackgroundColor(self):
        if not self.isMicaEffectEnabled():
            return self._darkBackgroundColor if isDarkTheme() else self._lightBackgroundColor
        return QColor(0, 0, 0, 0)

    def _onThemeChangedFinished(self):
        if self.isMicaEffectEnabled():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.backgroundColor)
        painter.drawRect(self.rect())

    def setMicaEffectEnabled(self, isEnabled: bool):
        if sys.platform != 'win32' or sys.getwindowsversion().build < 22000:
            return
        self._isMicaEnabled = isEnabled
        if isEnabled:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        else:
            self.windowEffect.removeBackgroundEffect(self.winId())
        self.setBackgroundColor(self._normalBackgroundColor())

    def isMicaEffectEnabled(self):
        return self._isMicaEnabled

    def resizeEvent(self, e):
        self.titleBar.move(20, 0)
        self.titleBar.resize(self.width() - 20, self.titleBar.height())

    def switch_widget(self, index):
        self.dock_widget.switch_widget(index)
        if not self.dock_widget.dock_show:
            self.splitter.setSizes([int(self.width() * 1), int(self.width() * 0)])
        else:
            self.splitter.setSizes([int(self.width() * 0.9), int(self.width() * 0.1)])

    def hide_dock(self):
        self.splitter.setSizes([int(self.width() * 1), int(self.width() * 0)])

    def show_dock_menu(self):
        menu = QMenu()
        for env in self.env_history:
            action = menu.addAction(env.get('name'))
            action.triggered.connect(lambda checked: self.set_default_interpreter(env))
        create_action = menu.addAction("创建解释器")
        create_action.triggered.connect(self.show_create_venv_dialog)
        delete_action = menu.addAction("解释器管理")
        delete_action.triggered.connect(self.delete_virtual_environment)
        menu.exec(self.dock_btn.mapToGlobal(self.dock_btn.rect().bottomLeft()))

    def show_create_venv_dialog(self):
        dialog = CreateVenvMessageBox(self)
        dialog.mkenv_signal.connect(self.add_interpreter_to_histor)
        dialog.exec()

    def delete_virtual_environment(self):
        # TODO 待完善
        pass

    def set_default_interpreter(self, env):
        env_name = env.get('name')
        env_path = env.get('path')
        if env_name and env_path:
            MySettings.setValue("default_interpreter_name", env_name)
            MySettings.setValue("default_interpreter", env_path)
            self.dock_btn.setText(env_name)

    def remove_interpreter(self):
        # TODO 待完善
        pass

    def check_syntax(self):
        try:
            editor = self.user_interface.right_code.stacked_widget.currentWidget()
            if editor:
                editor.check_code()
                errors = editor.syntax_errors
                if errors != self.syntax_error:
                    self.syntax_error = errors
                    syntax_str = self.format_syntax_errors(errors)
                    self.dock_widget.info_widget.setText(syntax_str)
                else:
                    self.__changeTimer.stop()
        except Exception as e:
            logging.warning(e)

    def format_syntax_errors(self, errors):
        syntax_str = ""
        for error in errors:
            flag = "⚠️" if 'E' not in error.get('message-id') and 'F' not in error.get('message-id') else '❗️'
            start_line, start_index = error.get('line'), error.get('column')
            end_line, end_index = error.get('endLine'), error.get('endColumn')
            message_id, message = error.get('message-id'), error.get('message')
            symbol = error.get('symbol')
            if end_index is not None:
                syntax_str += (f'{flag}{message_id:>6}: {message},{symbol}({start_line:}:{start_index:}'
                               f'~{end_line:}:{end_index:})\n')
            else:
                syntax_str += f'{flag}{message_id:>6}: {message},{symbol}({start_line:})\n'
        return syntax_str

    def resetChangeTimer(self):
        self.__changeTimer.stop()
        self.__changeTimer.start()

    def load_env_history(self):
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as file:
                return json.load(file)
        return []

    def save_penv_history(self):
        with open(self.env_file, 'w') as file:
            json.dump(self.env_history, file, indent=4)

    def add_interpreter_to_histor(self, env_info: dict) -> None:
        self.env_history.append(env_info)
        self.save_penv_history()
