import os
import subprocess

from PyQt6.QtWidgets import QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox, QDialog

from util.find_python import find_python_paths


class CreateVenvDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("创建虚拟环境")
        self.setGeometry(0, 0, 200, 150)

        layout = QFormLayout()
        self.venv_path_input = QLineEdit()
        self.venv_path_input.setPlaceholderText("输入虚拟环境的路径")
        layout.addRow("路径:", self.venv_path_input)

        self.venv_name_input = QLineEdit()
        self.venv_name_input.setPlaceholderText("输入虚拟环境名称")
        layout.addRow("名称:", self.venv_name_input)

        self.python_selector = QComboBox()
        python_interpreters = find_python_paths()
        self.python_selector.addItems(python_interpreters)
        layout.addRow("基础解释器:", self.python_selector)

        self.create_btn = QPushButton("创建")
        self.create_btn.clicked.connect(self.create_virtual_environment)
        layout.addWidget(self.create_btn)

        self.setLayout(layout)

    def create_virtual_environment(self):
        venv_path = self.venv_path_input.text()
        venv_name = self.venv_name_input.text()
        base_interpreter = self.python_selector.currentText()
        if not venv_path or not venv_name or not base_interpreter:
            QMessageBox.warning(self, "Input Error",
                                "Please provide path, name, and select a base interpreter for the virtual environment.")
            return

        full_venv_path = os.path.join(venv_path, venv_name)
        try:
            subprocess.run([base_interpreter, '-m', 'venv', full_venv_path], check=True)
            interpreter_path = os.path.join(full_venv_path, 'Scripts',
                                            'python.exe') if os.name == 'nt' else os.path.join(full_venv_path, 'bin',
                                                                                               'python')
            self.parent().add_interpreter_to_history(interpreter_path)
            QMessageBox.information(self, "Success", f"Virtual environment created at {full_venv_path}")
            self.accept()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to create virtual environment:\n{e}")
