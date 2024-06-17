from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, \
    QMenu, QMessageBox, QInputDialog, QFileDialog
from PyQt6.QtCore import Qt, QDir

from view.CodeWindow import CodeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PythonPad ++")

        # 创建主窗口小部件和布局
        self.main_widget = QWidget()
        main_layout = QHBoxLayout(self.main_widget)

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

        # 将 QSplitter 添加到主布局
        main_layout.addWidget(self.splitter)

        self.setCentralWidget(self.main_widget)

        # 在调整窗口大小时更新 QSplitter 比例
        self.resizeEvent(None)

        # 创建菜单栏
        self.menubar = self.menuBar()

        # 创建文件菜单
        file_menu = QMenu("File", self)
        self.menubar.addMenu(file_menu)

        # 创建新建文件夹动作
        new_folder_action = QAction("新建项目", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        file_menu.addAction(new_folder_action)

        # 创建打开目录动作
        open_folder_action = QAction("打开项目", self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

    def resizeEvent(self, event):
        self.centralWidget().layout().itemAt(0).widget().setSizes([int(self.width() * 0.2), int(self.width() * 0.8)])
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
