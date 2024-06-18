import json
import os
import platform
from pathlib import PurePath
from venv import logger

from PyQt6.QtCore import pyqtSlot, QTimer, Qt, QPoint
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel, QDockWidget, QPushButton, \
    QWidget, QMenu, QStackedWidget, QTextEdit, QHBoxLayout, QMessageBox

from ui.style_sheet import CodeTabStyleSheet, CodeWindowStyleSheet, ButtonStyleSheet
from util.config import IMG_PATH
from view.Editor import Editor


class CodeWindow(QMainWindow):
    """
    代码窗口实现类
    """

    def __init__(self):
        super().__init__()
        self.dock_show = False
        self.syntax_error = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Code Window Demo')
        self.setStyleSheet(CodeWindowStyleSheet)

        # 创建 QTabWidget
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.setStyleSheet(CodeTabStyleSheet)
        self.tabs.currentChanged.connect(self.__resetChangeTimer)

        self.setCentralWidget(self.tabs)

        self.stacked_widget = QStackedWidget()

        self.info_widget = QTextEdit(self.stacked_widget)
        self.info_widget.setReadOnly(True)
        self.info_widget.setTextColor(QColor('black'))

        self.log_widget = QTextEdit(self.stacked_widget)
        self.log_widget.setReadOnly(True)

        self.stacked_widget.addWidget(self.info_widget)
        self.stacked_widget.addWidget(self.log_widget)

        self.infoDock = QDockWidget("Info Dock", self)
        self.infoDock.setWidget(self.stacked_widget)

        self.dock_title = QWidget()
        if platform.system() == 'Darwin':
            self.dock_title.setStyleSheet("background-color: rgb(255, 255, 255)")
        self.dock_title_layout = QHBoxLayout()
        self.dock_title.setLayout(self.dock_title_layout)
        self.dock_title_label = QLabel()
        self.dock_title_layout.addWidget(self.dock_title_label)
        self.dock_title_layout.addStretch()

        self.minimize_button = QPushButton()
        self.minimize_button.setStyleSheet(ButtonStyleSheet)
        self.minimize_button.setIcon(QIcon(str(IMG_PATH.joinpath(PurePath('mini_size.png')))))
        self.minimize_button.setFixedSize(20, 20)
        self.minimize_button.clicked.connect(self.dock_hide)
        self.dock_title_layout.addWidget(self.minimize_button)

        self.infoDock.setTitleBarWidget(self.dock_title)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.infoDock)

        self.infoDock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                                  QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.infoDock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.infoDock.hide()

        # 创建状态栏按钮
        self.toggleButton = self.create_status_button('syntax_info.png', self.switch_widget, 0)
        self.show_log_button = self.create_status_button('code_run.png', self.switch_widget, 1)

        self.__statusBar = self.statusBar()
        self.__statusBar.addPermanentWidget(self.toggleButton)
        self.__statusBar.addPermanentWidget(self.show_log_button)
        self.__statusBar.setFixedHeight(24)

        self.__changeTimer = QTimer()
        self.__changeTimer.timeout.connect(self.check_syntax)
        self.__changeTimer.start(5000)

    def create_status_button(self, icon_path, callback, index):
        button = QPushButton("", self)
        button.setCheckable(True)
        button.setChecked(True)
        button.setIcon(QIcon(str(IMG_PATH.joinpath(PurePath(icon_path)))))
        button.setStyleSheet(ButtonStyleSheet)
        button.clicked.connect(lambda: callback(index))
        return button

    def load_file(self, file_path):
        self.add_file_to_tabs(file_path)

    def add_file_to_tabs(self, file_path) -> Editor:
        editor = Editor(self.tabs)
        editor.load_file(file_path)
        editor.ctrl_left_click_signal.connect(self.handle_ctrl_left_click)
        editor.textChanged.connect(self.__resetChangeTimer)
        self.tabs.addTab(editor, file_path.split(os.sep)[-1])
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        self.__statusBar.show()
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
        try:
            editor.save_file()
        except Exception as e:
            logger.warning(e)
        self.info_widget.setText('')
        self.tabs.removeTab(index)
        self.dock_hide()
        editor.deleteLater()
        if self.tabs.count() == 0:
            self.__statusBar.hide()

    def handle_ctrl_left_click(self, addrs: dict):
        assign_addr = addrs.get("assign_addr")
        reference_addr = addrs.get("reference_addr")
        current_tab = self.tabs.currentWidget()
        if assign_addr:
            path = assign_addr.get('ModulePath')
            line = assign_addr.get('Line')
            index = assign_addr.get('Column')
            self.dock_hide()
            if path != current_tab.current_file_path:
                self.jump_to_assign_tab(path, line, index)
            else:
                self.jump_to_assign_line(line, index)
        elif reference_addr:
            self.dock_hide()
            self.show_reference_menu(reference_addr, current_tab)
        current_tab.setSelection(0, 0, 0, 0)

    def show_reference_menu(self, reference_addr, current_tab):
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

    def check_syntax(self):
        if self.tabs.currentWidget():
            editor = self.tabs.currentWidget()
            editor.check_code()
            errors, syntax_str = editor.syntax_errors, ""
            if errors != self.syntax_error:
                if errors:
                    self.syntax_error = errors
                    for error in errors:
                        flag = "⚠️" if 'E' not in error.get('message-id') and 'F' not in error.get(
                            'message-id') else '❗️'
                        start_line, start_index = error.get('line'), error.get('column')
                        end_line, end_index = error.get('endLine'), error.get('endColumn')
                        message_id, message = error.get('message-id'), error.get('message')
                        symbol = error.get('symbol')
                        if end_index is not None:
                            syntax_str += (f'{flag}{message_id:>6}: {message},{symbol}({start_line:}:{start_index:}'
                                           f'~{end_line:}:{end_index:})\n')
                        else:
                            syntax_str += f'{flag}{message_id:>6}: {message},{symbol}({start_line:})\n'
                    self.info_widget.setText(syntax_str)
            else:
                self.__changeTimer.stop()

    def __resetChangeTimer(self):
        self.__changeTimer.stop()
        self.__changeTimer.start()

    def reference_jump(self, jump_info: dict):
        path, line, column = jump_info.get('ModulePath'), jump_info.get('Line'), jump_info.get('Column')
        self.jump_to_assign_tab(path, line, column)

    def switch_widget(self, index):
        if not self.dock_show:
            self.infoDock.show()
            self.dock_show = True
        elif self.stacked_widget.currentIndex() == index:
            self.infoDock.hide()
            self.dock_show = False
        self.stacked_widget.setCurrentIndex(index)

    def dock_hide(self):
        self.infoDock.hide()
        self.dock_show = False
