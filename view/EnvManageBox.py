import json
import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QMainWindow
from qfluentwidgets import ComboBox, FluentIcon, RoundMenu, Action, TransparentDropDownPushButton, PushButton, \
    TableWidget, FlyoutViewBase

from conf.config import ROOT_PATH, MySettings
from view.CreateVenvMessageBox import CreateVenvMessageBox


class EnvManageBox(FlyoutViewBase):

    def __init__(self):
        super(EnvManageBox, self).__init__()
        self.setup_env()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout()
        self.top_widget.setLayout(self.top_layout)
        self.setup_top()
        self.setup_interpreter_info()

    def setup_env(self):
        self.env_file = ROOT_PATH / 'conf' / "env_history.json"
        self.env_history = self.load_env_history()
        self.env_path = MySettings.value("default_interpreter")
        if self.env_path and self.env_path.exists():
            pass

    def setup_top(self):
        self.line_edit = QLabel(self)
        self.line_edit.setText("Python解释器:")
        self.line_edit.setFixedWidth(88)
        self.top_layout.addWidget(self.line_edit)

        self.interpreter_list = ComboBox(self)
        self.interpreter_list.currentIndexChanged.connect(self.set_default_interpreter)
        self.setup_interpreter_list()
        self.top_layout.addWidget(self.interpreter_list)

        self.manage_button = TransparentDropDownPushButton(FluentIcon.MENU, '添加解释器')
        self.manage_button.setFixedWidth(188)
        menu = RoundMenu(parent=self.manage_button)
        menu.addAction(Action(FluentIcon.FLAG, '添加本地解释器', triggered=self.show_create_venv_dialog))
        menu.addAction(Action(FluentIcon.FLAG, 'SSH', triggered=lambda: print("TODO SSH")))
        menu.addAction(Action(FluentIcon.FLAG, 'Docker', triggered=lambda: print("TODO Docker")))
        self.manage_button.setMenu(menu)
        self.top_layout.addWidget(self.manage_button)

        self.main_layout.addWidget(self.top_widget)

    def setup_interpreter_info(self):
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout()
        self.bottom_widget.setLayout(self.bottom_layout)

        self.button_layout = QHBoxLayout()
        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_layout)
        self.install_button = PushButton("+")
        self.uninstall_button = PushButton("-")
        self.update_button = PushButton("⟳")
        self.button_layout.addWidget(self.install_button)
        self.button_layout.addWidget(self.uninstall_button)
        self.button_layout.addWidget(self.update_button)

        self.bottom_layout.addWidget(self.button_widget)

        self.interpreter_info = TableWidget(self)
        # 启用边框并设置圆角
        self.interpreter_info.setBorderVisible(True)
        self.interpreter_info.setBorderRadius(8)

        self.interpreter_info.setWordWrap(False)
        self.interpreter_info.setColumnWidth(0, 80)

        self.main_layout.addWidget(self.bottom_widget)
        self.main_layout.addWidget(self.interpreter_info)

    def setup_interpreter_list(self):
        for env in self.env_history:
            name = env.get('name')
            path = env.get('path')
            self.interpreter_list.addItem(f'{name} ({path})', userData=env)

    def load_env_history(self):
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as file:
                return json.load(file)
        return []

    def set_default_interpreter(self):
        index = self.interpreter_list.currentIndex()
        env = self.interpreter_list.itemData(index)
        env_name = env.get('name')
        env_path = env.get('path')
        if env_name and env_path:
            MySettings.setValue("default_interpreter_name", env_name)
            MySettings.setValue("default_interpreter", env_path)

    def save_env_history(self):
        with open(self.env_file, 'w') as file:
            json.dump(self.env_history, file, indent=4)

    def add_interpreter_to_histor(self, env_info: dict) -> None:
        self.env_history.append(env_info)
        self.save_env_history()

    def show_create_venv_dialog(self):
        dialog = CreateVenvMessageBox(self)
        dialog.mkenv_signal.connect(self.add_interpreter_to_histor)
        dialog.exec()
