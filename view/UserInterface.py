import json
import os
import sys

from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QMenu, QMessageBox, \
    QInputDialog, QFileDialog
from qfluentwidgets import TreeView, FluentIcon, DropDownPushButton, RoundMenu, Action

from util.config import MySettings, NotMac
from view.CodeWindow import CodeWindow


class UserInterface(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.history_file = "project_history.json"
        self.project_history = self.load_project_history()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        self.setup_menubar()
        self.setup_ui()
        if NotMac:
            self.top_widget.hide()
        self.display_project_history()
        self.resizeEvent(None)
        self.last_opened_file = None
        self.load_settings()
        if self.last_opened_file:
            self.open_project(self.last_opened_file)
            if NotMac:
                self.top_widget.show()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

    def setup_ui(self):
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        self.setup_left_widget()
        self.setup_right_widget()

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])

        self.main_layout.addWidget(self.splitter)
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
        self.right_widget.setStyleSheet("""
        background-color: rgb(255, 255, 255);
        border-radius: 7px;
        """)
        right_layout = QVBoxLayout(self.right_widget)
        self.right_code = CodeWindow(self)
        right_layout.addWidget(self.right_code)

    def setup_menubar_no_mac(self):
        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)
        self.top_widget.setFixedWidth(260)
        self.top_layout = QHBoxLayout()
        self.top_widget.setLayout(self.top_layout)

        self.top_file_button = DropDownPushButton(FluentIcon.FOLDER, "文件")
        file_menu = RoundMenu("文件", self.top_file_button)
        file_menu.setIcon(FluentIcon.FOLDER)
        file_menu.addAction(Action(FluentIcon.FOLDER, '新建项目', triggered=self.create_new_folder))
        file_menu.addAction(Action(FluentIcon.FOLDER, '打开项目', triggered=self.open_folder))
        self.top_file_button.setMenu(file_menu)
        self.top_layout.addWidget(self.top_file_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.top_layout.setContentsMargins(30, 0, 0, 0)

        self.top_project_button = DropDownPushButton(FluentIcon.PROJECTOR, "项目")
        self.project_menu = RoundMenu('项目', self.top_project_button)
        self.project_menu.setIcon(FluentIcon.PROJECTOR)
        self.top_project_button.setMenu(self.project_menu)
        self.top_layout.addWidget(self.top_project_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.top_project_button.setContentsMargins(160, 0, 0, 0)
        self.top_layout.setSpacing(0)
        self.main_layout.addWidget(self.top_widget)

    def setup_menubar_mac(self):
        self.menubar = self.menuBar()
        file_menu = QMenu("文件", self)
        self.menubar.addMenu(file_menu)
        project_name = MySettings.value("lastProject")[-1]['name']
        if project_name:
            self.project_menu = QMenu(project_name, self)
        else:
            self.project_menu = QMenu("项目", self)
        self.menubar.addMenu(self.project_menu)

        new_folder_action = QAction("新建项目", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        file_menu.addAction(new_folder_action)

        open_folder_action = QAction("打开项目", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

    def setup_menubar(self):
        if NotMac:
            self.setup_menubar_no_mac()
        else:
            self.setup_menubar_mac()

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
            if NotMac:
                self.project_menu.addAction(Action(
                    FluentIcon.PROJECTOR, project['name'],
                    triggered=lambda checked, path=project['path']: self.open_project(path)))
            else:
                action = QAction(project['name'], self)
                action.triggered.connect(lambda checked, path=project['path']: self.open_project(path))
                self.project_menu.addAction(action)

    def open_project(self, path):
        if os.path.exists(path):
            self.tree_view.setRootIndex(self.file_system_model.index(path))
            self.last_opened_file = path
            if NotMac is False:
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
