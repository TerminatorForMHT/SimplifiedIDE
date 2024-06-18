from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QAction, QFileSystemModel
from PyQt6.QtWidgets import QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, \
    QMenu, QMessageBox, QInputDialog, QFileDialog

from ui.style_sheet import TreeStyleSheetForMac
from view.CodeWindow import CodeWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PythonPad ++")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setup_ui()
        self.setup_menubar()
        self.resizeEvent(None)

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
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setStyleSheet(TreeStyleSheetForMac)
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
        file_menu = QMenu("File", self)
        self.menubar.addMenu(file_menu)

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
            self.tree_view.setRootIndex(self.file_system_model.index(folder_path))

    def on_tree_view_double_clicked(self, index):
        if not self.file_system_model.isDir(index):
            file_path = self.file_system_model.filePath(index)
            try:
                self.right_code.load_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}\n{str(e)}")
