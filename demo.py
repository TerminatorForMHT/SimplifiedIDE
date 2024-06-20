import sys
import os
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
                             QMessageBox, QLineEdit, QDockWidget, QMenu, QDialog, QFormLayout,QComboBox)

from util.find_python import find_python_paths


class CreateVenvDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Create Virtual Environment")
        self.setGeometry(400, 400, 400, 200)

        layout = QFormLayout()
        self.venv_path_input = QLineEdit()
        self.venv_path_input.setPlaceholderText("Enter path to create virtual environment")
        layout.addRow("Path:", self.venv_path_input)

        self.venv_name_input = QLineEdit()
        self.venv_name_input.setPlaceholderText("Enter name for virtual environment")
        layout.addRow("Name:", self.venv_name_input)

        self.python_selector = QComboBox()
        python_interpreters = find_python_paths()
        self.python_selector.addItems(python_interpreters)
        layout.addRow("Base Interpreter:", self.python_selector)

        self.create_btn = QPushButton("Create")
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


class InterpreterManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Interpreter Manager')
        self.setGeometry(300, 300, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.interpreter_list = QListWidget()
        layout.addWidget(self.interpreter_list)

        self.default_label = QLabel('Default Interpreter: None')
        layout.addWidget(self.default_label)

        # Dock widget for managing virtual environments
        self.dock = QDockWidget("Virtual Environment Management", self)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock)

        self.dock_btn = QPushButton('Manage Virtual Environments')
        self.dock_btn.clicked.connect(self.show_dock_menu)
        dock_layout = QVBoxLayout()
        dock_layout.addWidget(self.dock_btn)
        dock_widget = QWidget()
        dock_widget.setLayout(dock_layout)
        self.dock.setWidget(dock_widget)

        self.history_menu = QMenu("History", self)

    def show_dock_menu(self):
        menu = QMenu()
        history_action = menu.addAction("History")
        history_action.triggered.connect(self.show_history)
        create_action = menu.addAction("Create Virtual Environment")
        create_action.triggered.connect(self.show_create_venv_dialog)
        delete_action = menu.addAction("Delete Virtual Environment")
        delete_action.triggered.connect(self.delete_virtual_environment)
        menu.exec(self.dock_btn.mapToGlobal(self.dock_btn.rect().bottomLeft()))

    def show_history(self):
        menu = QMenu()
        for index in range(self.interpreter_list.count()):
            interpreter = self.interpreter_list.item(index).text()
            action = menu.addAction(interpreter)
            action.triggered.connect(lambda checked, interp=interpreter: self.set_default_interpreter(interp))
        menu.exec(self.dock_btn.mapToGlobal(self.dock_btn.rect().bottomLeft()))

    def show_create_venv_dialog(self):
        dialog = CreateVenvDialog(self)
        dialog.exec()

    def delete_virtual_environment(self):
        selected_item = self.interpreter_list.currentItem()
        if selected_item:
            interpreter_path = selected_item.text()
            confirm = QMessageBox.question(self, "Confirm Delete",
                                           f"Are you sure you want to delete {interpreter_path}?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.interpreter_list.takeItem(self.interpreter_list.row(selected_item))
                if self.default_label.text().split(": ")[1] == interpreter_path:
                    self.default_label.setText('Default Interpreter: None')
                # Optionally remove the virtual environment directory here if desired

    def add_interpreter(self, interpreter_path):
        if interpreter_path:
            self.add_interpreter_to_history(interpreter_path)

    def add_interpreter_to_history(self, interpreter_path):
        if not any(
                self.interpreter_list.item(i).text() == interpreter_path for i in range(self.interpreter_list.count())):
            self.interpreter_list.addItem(interpreter_path)

    def set_default_interpreter(self, interpreter_path=None):
        if interpreter_path is None:
            selected_item = self.interpreter_list.currentItem()
            if selected_item:
                interpreter_path = selected_item.text()
        if interpreter_path:
            self.default_label.setText(f'Default Interpreter: {interpreter_path}')

    def remove_interpreter(self):
        selected_item = self.interpreter_list.currentItem()
        if selected_item:
            self.interpreter_list.takeItem(self.interpreter_list.row(selected_item))
            if self.default_label.text().split(": ")[1] == selected_item.text():
                self.default_label.setText('Default Interpreter: None')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InterpreterManager()
    ex.show()
    sys.exit(app.exec())
