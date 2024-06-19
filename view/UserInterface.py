import json
import os

from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QMenu, QMessageBox, \
    QInputDialog, QFileDialog
from qfluentwidgets import TreeView

from util.config import MySettings
from view.CodeWindow import CodeWindow


class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.history_file = "project_history.json"
        self.project_history = self.load_project_history()

        self.setup_ui()
        self.setup_menubar()
        self.display_project_history()
        self.resizeEvent(None)
        self.last_opened_file = None
        self.load_settings()
        if self.last_opened_file:
            self.open_project(self.last_opened_file)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

    def setup_ui(self):
        self.main_widget = QWidget()
        main_layout = QHBoxLayout(self.main_widget)

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.setup_left_widget()
        self.setup_right_widget()

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])

        main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.main_widget)

    def setup_left_widget(self):
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)
        self.tree_view = TreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setHeaderHidden(True)
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)
        left_layout.addWidget(self.tree_view)

    def setup_right_widget(self):
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        self.right_code = CodeWindow()
        right_layout.addWidget(self.right_code)

    def setup_menubar(self):
        self.menubar = self.menuBar()
        file_menu = QMenu("文件", self)
        self.menubar.addMenu(file_menu)
        try:
            project_name = MySettings.value("lastProject")
            if project_name:
                self.project_menu = QMenu(project_name, self)
            else:
                self.project_menu = QMenu("项目", self)
            self.project_menu = QMenu(project_name, self)
        except Exception:
            self.project_menu = QMenu("项目", self)
        self.menubar.addMenu(self.project_menu)

        new_folder_action = QAction("新建项目", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        file_menu.addAction(new_folder_action)

        open_folder_action = QAction("打开项目", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

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
            project_name = os.path.basename(folder_path)
            self.tree_view.setRootIndex(self.file_system_model.index(folder_path))
            self.add_project_to_history(project_name, folder_path)
            self.last_opened_file = folder_path
            self.project_name = project_name
            self.project_menu.setTitle(project_name)
            MySettings.setValue("project_path", folder_path)
            self.save_settings()

    def on_tree_view_double_clicked(self, index):
        if not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            try:
                self.right_code.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")

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
            action = QAction(project['name'], self)
            action.triggered.connect(lambda checked, path=project['path']: self.open_project(path))
            self.project_menu.addAction(action)

    def open_project(self, path):
        if os.path.exists(path):
            self.tree_view.setRootIndex(self.file_system_model.index(path))
            self.last_opened_file = path
            self.project_name = os.path.basename(path)
            self.project_menu.setTitle(self.project_name)
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
