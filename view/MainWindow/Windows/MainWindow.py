import sys

from BlurWindow.blurWindow import GlobalBlur
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
    QMenu, QMessageBox, QInputDialog, QFileDialog, QToolBar, QPushButton, QApplication, QStyle
)

from ui.style_sheet import TreeStyleSheet, ButtonStyleSheet, ExitButtonStyleSheet
from view.CodeWindow import CodeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(500, 400)
        self.is_maximized = True

        self.setWindowTitle("PythonPad ++")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        GlobalBlur(self.winId(), Dark=True, QWidget=self)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        self.setup_ui()
        self.setup_actions()

    def setup_ui(self):
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        top_layout = QHBoxLayout()

        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)
        self.top_widget.setLayout(top_layout)

        self.menubar = self.menuBar()
        self.file_menu = QMenu("文件", self)
        self.menubar.addMenu(self.file_menu)
        top_layout.addWidget(self.menubar)

        toolbar = QToolBar("Custom Toolbar", self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        top_layout.addWidget(toolbar)

        self.setup_toolbar(toolbar)

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setup_splitter()

        main_layout.addWidget(self.top_widget)
        main_layout.addWidget(self.splitter)
        self.setCentralWidget(self.main_widget)

        self.resizeEvent(None)

    def setup_toolbar(self, toolbar):
        # 获取系统默认的图标
        minimize_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton)
        maximize_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        close_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        self.minimizi_button, self.maximize_button = QPushButton('', self), QPushButton('', self)
        self.close_button = QPushButton('', self)
        buttons = [self.minimizi_button, self.maximize_button, self.close_button]
        icons = [minimize_icon, maximize_icon, close_icon]
        actions = [self.showMinimized, self.toggle_maximize_restore, self.close]
        styles = [ButtonStyleSheet, ButtonStyleSheet, ExitButtonStyleSheet]

        for button, icon, action, style in zip(buttons, icons, actions, styles):
            button.setIcon(icon)
            button.setStyleSheet(style)
            button.clicked.connect(action)
            toolbar.addWidget(button)

    def setup_splitter(self):
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)

        self.tree_view = QTreeView()
        left_layout.addWidget(self.tree_view)
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setStyleSheet(TreeStyleSheet)
        self.tree_view.setHeaderHidden(True)
        for col in range(1, 4):
            self.tree_view.setColumnHidden(col, True)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)

        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        self.right_code = CodeWindow()
        right_layout.addWidget(self.right_code)

        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])

    def setup_actions(self):
        actions = [("新建项目", self.create_new_folder), ("打开项目", self.open_folder)]
        for name, method in actions:
            action = QAction(name, self)
            action.triggered.connect(method)
            self.file_menu.addAction(action)

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

    def on_tree_view_double_clicked(self, index):
        if not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            try:
                self.right_code.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")

    def toggle_maximize_restore(self):
        maximize_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        restore_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
        if self.is_maximized:
            self.showNormal()
            self.maximize_button.setIcon(maximize_icon)
        else:
            self.showMaximized()
            self.maximize_button.setIcon(restore_icon)
        self.is_maximized = not self.is_maximized

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.activateWindow()
