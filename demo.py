import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)


class PackageManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.interpreter_label = QLabel("Python 解释器:", self)
        self.interpreter_combo = QComboBox(self)
        self.interpreter_combo.addItems(["Python 3.9 (simple-editor) - /Project/simple-editor/venv/bin/python"])

        self.add_interpreter_button = QPushButton("添加解释器", self)

        self.package_table = QTableWidget(self)
        self.package_table.setColumnCount(3)
        self.package_table.setHorizontalHeaderLabels(["软件包", "版本", "最新版本"])
        self.package_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.package_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.package_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.load_packages()

        self.action_layout = QHBoxLayout()
        self.install_button = QPushButton("+", self)
        self.uninstall_button = QPushButton("-", self)
        self.update_button = QPushButton("⟳", self)

        self.action_layout.addWidget(self.install_button)
        self.action_layout.addWidget(self.uninstall_button)
        self.action_layout.addWidget(self.update_button)

        layout.addWidget(self.interpreter_label)
        layout.addWidget(self.interpreter_combo)
        layout.addWidget(self.add_interpreter_button)
        layout.addLayout(self.action_layout)
        layout.addWidget(self.package_table)

        self.setLayout(layout)

    def load_packages(self):
        packages = [
            ("MarkupSafe", "2.1.5", "2.1.5"),
            ("PyCocoa", "23.12.28", "23.12.28"),
            ("PyQt6", "6.7.0", "6.7.2"),
            ("PyQt6-Fluent-Widgets", "1.5.7", "1.5.8"),
            ("PyQt6-Frameless-Window", "0.3.9", "0.3.9"),
            ("PyQt6-QScintilla", "2.14.1", "2.14.1"),
            ("PyQt6-sip", "13.6.0", "13.8.0"),
            ("QScintilla", "2.14.1", "2.14.1"),
            ("astroid", "3.2.2", "3.2.3"),
            ("autopep8", "2.1.0", "2.3.1"),
            ("beautifulsoup4", "4.12.3", "4.12.3"),
            ("blinker", "1.8.2", "1.8.2"),
            ("click", "8.1.7", "8.1.7"),
            ("darkdetect", "0.8.0", "0.8.0"),
            ("dill", "0.3.8", "0.3.8"),
            ("flask", "3.0.3", "3.0.3"),
            ("importlib-metadata", "7.1.0", "8.0.0"),
            ("isort", "5.13.2", "5.13.2"),
            ("itsdangerous", "2.2.0", "2.2.0"),
            ("jedi", "0.19.1", "0.19.1"),
            ("jinja2", "3.1.4", "3.1.4"),
            ("mccabe", "0.7.0", "0.7.0"),
        ]
        self.package_table.setRowCount(len(packages))
        for row, (pkg, ver, latest_ver) in enumerate(packages):
            self.package_table.setItem(row, 0, QTableWidgetItem(pkg))
            self.package_table.setItem(row, 1, QTableWidgetItem(ver))
            self.package_table.setItem(row, 2, QTableWidgetItem(latest_ver))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyCharm-like Python IDE")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Package management
        self.package_management = PackageManagement()
        self.layout.addWidget(self.package_management)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
