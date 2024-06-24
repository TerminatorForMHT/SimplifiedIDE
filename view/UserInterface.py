import json
import os

from PyQt6.QtCore import Qt, QDir, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QInputDialog, QFileDialog
from qfluentwidgets import TreeView, FluentIcon, DropDownPushButton, RoundMenu, Action

from conf.config import MySettings, ROOT_PATH
from view.CodeWidget import CodeWidget


class UserInterface(QWidget):
    open_file_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.history_file = ROOT_PATH / 'conf' / "project_history.json"
        self.project_history = self.load_project_history()
        self.last_opened_file = None
        self.init_ui()
        self.load_settings()
        if self.last_opened_file:
            self.open_project(self.last_opened_file)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.setup_menubar()
        self.setup_splitter()
        self.display_project_history()

    def setup_splitter(self):
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        self.tree_view = TreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        left_layout.addWidget(self.tree_view)
        self.splitter.addWidget(self.left_widget)

        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("background-color: rgb(255, 255, 255); border-radius: 7px;")
        right_layout = QVBoxLayout(self.right_widget)
        self.right_code = CodeWidget(self)
        right_layout.addWidget(self.right_code)
        self.splitter.addWidget(self.right_widget)

        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])

    def setup_menubar(self):
        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)
        self.top_widget.setFixedWidth(260)
        self.top_layout = QHBoxLayout(self.top_widget)
        self.top_widget.setLayout(self.top_layout)
        self.main_layout.addWidget(self.top_widget)

        self.top_file_button = self.create_menu_button("文件", FluentIcon.FOLDER, [
            ("新建项目", self.create_new_folder),
            ("打开项目", self.open_folder)
        ])
        self.top_layout.addWidget(self.top_file_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.top_project_button = DropDownPushButton(FluentIcon.PROJECTOR, "项目")
        self.project_menu = RoundMenu('项目', self.top_project_button)
        self.top_project_button.setMenu(self.project_menu)
        self.top_layout.addWidget(self.top_project_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.top_layout.setSpacing(0)

    def create_menu_button(self, text, icon, actions):
        button = DropDownPushButton(icon, text)
        menu = RoundMenu(text, button)
        menu.setIcon(icon)
        for action_text, action_method in actions:
            menu.addAction(Action(icon, action_text, triggered=action_method))
        button.setMenu(menu)
        return button

    def resizeEvent(self, event):
        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])
        if event:
            super().resizeEvent(event)

    def create_new_folder(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No directory selected!")
            return

        dir_path = self.file_system_model.filePath(index)
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter the name of the new folder:")
        if ok and folder_name:
            QDir(dir_path).mkdir(folder_name)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.homePath())
        if folder_path:
            self.tree_view.setRootIndex(self.file_system_model.index(folder_path))
            self.add_project_to_history(os.path.basename(folder_path), folder_path)
            self.last_opened_file = folder_path
            MySettings.setValue("project_path", folder_path)
            self.save_settings()

    def on_tree_view_double_clicked(self, index):
        if not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            try:
                self.right_code.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")
            self.open_file_signal.emit()

    def load_project_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                return json.load(file)
        return []

    def save_project_history(self):
        with open(self.history_file, 'w') as file:
            json.dump(self.project_history, file, indent=4)

    def add_project_to_history(self, name, path):
        project = {"name": name, "path": path}
        if project not in self.project_history:
            self.project_history.append(project)
            self.save_project_history()
            self.display_project_history()

    def display_project_history(self):
        self.project_menu.clear()
        for project in self.project_history:
            self.project_menu.addAction(Action(
                FluentIcon.PROJECTOR, project['name'],
                triggered=lambda checked, path=project['path']: self.open_project(path)))

    def open_project(self, path):
        if os.path.exists(path):
            self.tree_view.setRootIndex(self.file_system_model.index(path))
            self.last_opened_file = path
            self.save_settings()
        else:
            QMessageBox.warning(self, "Warning", f"The project path {path} does not exist.")
            self.project_history = [proj for proj in self.project_history if proj['path'] != path]
            self.save_project_history()
            self.display_project_history()

    def load_settings(self):
        self.last_opened_file = MySettings.value("lastOpenedFile")
        self.project_history = self.load_project_history()

    def save_settings(self):
        MySettings.setValue("lastProject", self.project_history)
        MySettings.setValue("lastOpenedFile", self.last_opened_file)
