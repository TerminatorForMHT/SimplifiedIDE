import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, ComboBox

from util.common_method import find_python_paths, create_and_activate_virtual_environment


class CreateVenvMessageBox(MessageBoxBase):
    """ Custom message box """

    mkenv_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")
        self.titleLabel = SubtitleLabel('创建虚拟环境')
        self.path_input = LineEdit()
        self.name_input = LineEdit()

        self.name_input.setPlaceholderText('请输入虚拟环境名称')
        self.name_input.setClearButtonEnabled(True)

        self.path_input.setPlaceholderText('请输入虚拟环境的路径')
        self.path_input.setClearButtonEnabled(True)

        self.python_selector = ComboBox()
        self.python_selector.setPlaceholderText('选择基础解释器')
        self.python_selector.addItems(find_python_paths())
        self.python_selector.setCurrentIndex(-1)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.name_input)
        self.viewLayout.addWidget(self.path_input)
        self.viewLayout.addWidget(self.python_selector)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)

        self.yesButton.clicked.connect(self.create_virtual_environment)

    def create_virtual_environment(self):
        venv_path = self.path_input.text()
        venv_name = self.name_input.text()
        base_interpreter = self.python_selector.currentText()

        if not venv_path or not venv_name or not base_interpreter:
            QMessageBox.warning(self, "Input Error", "请提供路径、名称，并选择基础解释器。")
            return

        full_venv_path = os.path.join(venv_path, venv_name)
        ret = create_and_activate_virtual_environment(full_venv_path, venv_name, base_interpreter)
        if ret[0] == 0:
            QMessageBox.information(self, '创建成功', ret[1])
        else:
            QMessageBox.warning(self, "创建失败", ret[1])
