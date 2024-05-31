import os
import sys
from pathlib import PurePath

from PyQt6.QtCore import pyqtSlot, QTimer, Qt, QPoint
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QFileDialog, QLabel, QDockWidget, QPushButton, \
    QWidget, QMenu, QScrollArea, QVBoxLayout

from ui.style_sheet import CodeTabStyleSheet, CodeWindowStyleSheet, CodeLabelStyleSheet, ButtonStyleSheet
from util.config import IMG_PATH, LoadFileType

from view.Editor import Editor


class CodeWindow(QMainWindow):
    """
    代码窗口实现类
    """

    def __init__(self):
        super().__init__()
        self.infoLabelIsVisible = False

        self.setWindowTitle('Code Window Demo')
        self.setStyleSheet(CodeWindowStyleSheet)

        # 添加“打开”菜单项
        open_action = QAction(QIcon('open_icon.png'), 'Open', self)
        open_action.triggered.connect(self.open_file)

        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction(open_action)

        # 创建 QTabWidget
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.setStyleSheet(CodeTabStyleSheet)

        self.setCentralWidget(self.tabs)

        self.infoLabel = QLabel("This is the bottom label")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.infoLabel.setStyleSheet(CodeLabelStyleSheet)

        self.infoDock = QDockWidget("Info Dock", self)

        self.scrollArea = QScrollArea(self.infoDock)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.infoLabel)

        layout = QVBoxLayout()
        layout.addWidget(self.infoLabel)
        self.scrollArea.setLayout(layout)

        self.infoDock.setWidget(self.scrollArea)
        self.infoDock.setTitleBarWidget(QWidget())

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.infoDock)

        self.infoDock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                                  QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.infoDock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)

        # 创建按钮
        self.toggleButton = QPushButton("", self)
        self.toggleButton.setCheckable(True)  # 设置按钮为可切换的
        self.toggleButton.setChecked(True)  # 默认显示底部文本框
        icon = str(IMG_PATH.joinpath(PurePath('Exclamation.png')))
        self.toggleButton.setIcon(QIcon(icon))
        self.toggleButton.setStyleSheet(ButtonStyleSheet)
        self.toggleButton.clicked.connect(self.toggleInfoLabel)

        # 在状态栏上添加按钮
        self.__statusBar = self.statusBar()
        self.__statusBar.addPermanentWidget(self.toggleButton)
        self.__statusBar.setFixedHeight(24)
        self.__statusBar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.__changeTimer = QTimer()
        self.__changeTimer.timeout.connect(self.check_syntax)
        self.__changeTimer.start(5000)

    def load_file(self, file_path):
        self.add_file_to_tabs(file_path)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', LoadFileType)
        if file_path:
            self.add_file_to_tabs(file_path)

    def add_file_to_tabs(self, file_path) -> Editor:
        editor = Editor(self.tabs)
        editor.load_file(file_path)
        editor.ctrl_left_click_signal.connect(self.handle_ctrl_left_click)
        editor.textChanged.connect(self.__resetChangeTimer)
        self.tabs.addTab(editor, file_path.split(os.sep)[-1])
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        self.scrollArea.show()
        return editor

    def jump_to_assign_tab(self, file_path, line, index):
        editor = self.add_file_to_tabs(file_path)
        editor.move_cursor_visible(line, index)

    def jump_to_assign_line(self, line, index):
        current_tab = self.tabs.currentWidget()
        current_tab.move_cursor_visible(line, index)

    @pyqtSlot(int)
    def closeTab(self, index):
        editor = self.tabs.widget(index)
        editor.save_file()
        self.infoLabel.setText('')
        self.scrollArea.hide()
        self.tabs.removeTab(index)
        editor.deleteLater()

    def handle_ctrl_left_click(self, addrs: dict):
        assign_addr = addrs.get("assign_addr")
        reference_addr = addrs.get("reference_addr")
        current_tab = self.tabs.currentWidget()
        if assign_addr:
            path = assign_addr.get('ModulePath')
            line = assign_addr.get('Line')
            index = assign_addr.get('Column')
            if path != current_tab.current_file_path:
                self.jump_to_assign_tab(path, line, index)
            else:
                self.jump_to_assign_line(line, index)
        elif reference_addr:
            menu = QMenu(self)
            icon = str(IMG_PATH.joinpath(PurePath('python.png')))
            for item in reference_addr:
                file = item.get('ModulePath').split(os.sep)[-1]
                line, code = item.get('Line'), item.get('Code')
                item_info = f'{file}    {line}   {code}'
                action = QAction(QIcon(icon), item_info, current_tab)
                action.triggered.connect(lambda: self.reference_jump(item))
                menu.addAction(action)
            line, index = current_tab.get_cursor_pos()
            global_pos = self.mapToGlobal(
                QPoint(current_tab.SendScintilla(current_tab.SCI_POINTXFROMPOSITION, line, index),
                       current_tab.SendScintilla(current_tab.SCI_POINTYFROMPOSITION, line)))
            menu.exec(global_pos)
            menu.deleteLater()
        current_tab.setSelection(0, 0, 0, 0)

    def check_syntax(self):
        if self.tabs.currentWidget():
            editor = self.tabs.currentWidget()
            editor.check_code()
            errors, syntax_str = editor.syntax_errors, ""
            if errors:
                for error in errors:
                    flage = "⚠️"
                    start_line, start_index = error.get('line'), error.get('column')
                    end_line, end_index = error.get('endLine'), error.get('endColumn')
                    message_id, message = error.get('message-id'), error.get('message')
                    symbol = error.get('symbol')
                    if 'E' in error.get('message-id') or 'F' in error.get('message-id'):
                        flage = '❗️'
                    if end_index is not None:
                        syntax_str += (f'{flage}{message_id:>6}: {message},{symbol}({start_line:}:{start_index:}'
                                       f'~{end_line:}:{end_index:})\n')
                    else:
                        syntax_str += f'{flage}{message_id:>6}: {message},{symbol}({start_line:})\n'
                self.infoLabel.setText(syntax_str)

    def __resetChangeTimer(self):
        """
        Private slot to reset the parse timer.
        """
        self.__changeTimer.stop()
        self.__changeTimer.start()

    def toggleInfoLabel(self):
        if self.toggleButton.isChecked():
            self.scrollArea.show()
        else:
            self.scrollArea.hide()

    def reference_jump(self, jump_info: dict):
        """
        跳转到引用位置
        """
        path, line, column = jump_info.get('ModulePath'), jump_info.get('Line'), jump_info.get('Column')
        self.jump_to_assign_tab(path, line, column)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = CodeWindow()
    main_window.showMaximized()

    sys.exit(app.exec())
