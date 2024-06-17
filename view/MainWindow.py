from pathlib import PurePath

from BlurWindow.blurWindow import GlobalBlur
from PyQt6.QtGui import QAction, QFileSystemModel, QIcon
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, \
    QMenu, QMessageBox, QInputDialog, QFileDialog, QToolBar, QPushButton
from PyQt6.QtCore import Qt, QDir

from ui.style_sheet import TreeStyleSheet, ButtonStyleSheet, ExitButtonStyleSheet
from util.config import IMG_PATH
from view.CodeWindow import CodeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_maximized = True

        self.setWindowTitle("PythonPad ++")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 400)

        GlobalBlur(self.winId(), Dark=True, QWidget=self)

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0)")

        # 创建主窗口小部件和布局
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)

        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)
        top_layout = QHBoxLayout(self.top_widget)
        self.top_widget.setLayout(top_layout)

        menubar = self.menuBar()
        # 创建文件菜单
        file_menu = QMenu("文件", self)
        menubar.addMenu(file_menu)
        top_layout.addWidget(menubar)

        # 创建一个工具栏并设置它也在顶部
        toolbar = QToolBar("Custom Toolbar", self)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)  # 显示按钮旁的文字
        self.addToolBar(toolbar)  # 默认就是TopToolBarArea，所以这里可以不用显式指定  # 左侧添加工具栏
        top_layout.addWidget(toolbar)

        # 创建新建文件夹动作
        new_folder_action = QAction("新建项目", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        file_menu.addAction(new_folder_action)

        # 创建打开目录动作
        open_folder_action = QAction("打开项目", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        # 在文件菜单中添加最小化、最大化和关闭的 QAction
        mini_ico = QIcon(str(IMG_PATH.joinpath(PurePath('mini_size.png'))))
        minimize_action = QPushButton('', self)
        minimize_action.setIcon(mini_ico)
        minimize_action.setStyleSheet(ButtonStyleSheet)
        minimize_action.clicked.connect(self.showMinimized)
        toolbar.addWidget(minimize_action)

        max_ico = QIcon(str(IMG_PATH.joinpath(PurePath('maxsize.png'))))
        maximize_action = QPushButton('', self)
        maximize_action.setIcon(max_ico)
        maximize_action.setStyleSheet(ButtonStyleSheet)
        maximize_action.clicked.connect(self.toggle_maximize_restore)
        toolbar.addWidget(maximize_action)

        exit_ico = QIcon(str(IMG_PATH.joinpath(PurePath('close.png'))))
        exit_action = QPushButton('', self)
        exit_action.setIcon(exit_ico)
        exit_action.setStyleSheet(ExitButtonStyleSheet)
        exit_action.clicked.connect(self.close)  # 关闭窗口的槽函数
        toolbar.addWidget(exit_action)

        # 创建 QFileSystemModel
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        # 创建 QSplitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 创建左边和右边的小部件
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.tree_view = QTreeView()
        self.left_layout.addWidget(self.tree_view)

        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setStyleSheet(TreeStyleSheet)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)  # 隐藏 Size 列
        self.tree_view.setColumnHidden(2, True)  # 隐藏 Type 列
        self.tree_view.setColumnHidden(3, True)  # 隐藏 Date Modified 列
        # 设置初始根目录
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_code = CodeWindow()
        self.right_layout.addWidget(self.right_code)

        # 将小部件添加到 QSplitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)

        # 设置默认比例
        self.splitter.setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])

        main_layout.addWidget(self.top_widget)
        # 将 QSplitter 添加到主布局
        main_layout.addWidget(self.splitter)

        self.setCentralWidget(self.main_widget)

        # 在调整窗口大小时更新 QSplitter 比例
        self.resizeEvent(None)

    def resizeEvent(self, event):
        self.centralWidget().layout().itemAt(1).widget().setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])
        if event:
            super().resizeEvent(event)

    def create_new_folder(self):
        # 获取当前选中的索引
        index = self.tree_view.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Warning", "No directory selected!")
            return

        # 获取选中目录的路径
        dir_path = self.file_system_model.filePath(index)

        # 显示输入对话框以获取新文件夹的名称
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter the name of the new folder:")
        if ok and folder_name:
            new_folder_path = QDir(dir_path).filePath(folder_name)
            QDir().mkdir(new_folder_path)

    def open_folder(self):
        # 显示打开文件夹对话框
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.homePath())
        if folder_path:
            self.tree_view.setRootIndex(self.file_system_model.index(folder_path))

    def on_tree_view_double_clicked(self, index):
        if self.file_system_model.isDir(index):
            return
        file_path = self.file_system_model.filePath(index)
        try:
            self.right_code.load_file(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")

    def toggle_maximize_restore(self):
        if not self.is_maximized:
            self.showMaximized()
            self.is_maximized = True
        else:
            self.showNormal()
            self.is_maximized = False

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.activateWindow()
