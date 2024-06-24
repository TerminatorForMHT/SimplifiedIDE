import os
import subprocess

from PyQt6.QtWidgets import QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox, QDialog

from util.common_method import find_python_paths


class CreateVenvDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("创建虚拟环境")
        self.setGeometry(0, 0, 200, 150)

        layout = QFormLayout(self)
        self.venv_path_input = QLineEdit(placeholderText="输入虚拟环境的路径")
        self.venv_name_input = QLineEdit(placeholderText="输入虚拟环境名称")
        self.python_selector = QComboBox()
        self.python_selector.addItems(find_python_paths())

        layout.addRow("路径:", self.venv_path_input)
        layout.addRow("名称:", self.venv_name_input)
        layout.addRow("基础解释器:", self.python_selector)

        create_btn = QPushButton("创建", clicked=self.create_virtual_environment)
        layout.addWidget(create_btn)

    def create_virtual_environment(self):
        venv_path = self.venv_path_input.text()
        venv_name = self.venv_name_input.text()
        base_interpreter = self.python_selector.currentText()

        if not venv_path or not venv_name or not base_interpreter:
            QMessageBox.warning(self, "Input Error", "请提供路径、名称，并选择基础解释器。")
            return

        full_venv_path = os.path.join(venv_path, venv_name)
        try:
            subprocess.run([base_interpreter, '-m', 'venv', full_venv_path], check=True)
            interpreter_path = os.path.join(full_venv_path, 'Scripts',
                                            'python.exe') if os.name == 'nt' else os.path.join(full_venv_path, 'bin',
                                                                                               'python')
            self.parent().add_interpreter_to_history(interpreter_path)
            QMessageBox.information(self, "Success", f"虚拟环境已创建于 {full_venv_path}")
            self.accept()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"创建虚拟环境失败:\n{e}")
