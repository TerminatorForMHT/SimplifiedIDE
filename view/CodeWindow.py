import os
from pathlib import PurePath
from venv import logger

from PyQt6.QtCore import pyqtSlot, QTimer, Qt, QPoint
from PyQt6.QtGui import QAction, QIcon, QColor
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QDockWidget, QPushButton, \
    QMenu, QStackedWidget, QMessageBox, QListWidget, QLabel, QVBoxLayout
from qfluentwidgets import TextEdit

from ui.style_sheet import CodeTabStyleSheet, CodeWindowStyleSheet, ButtonStyleSheet
from util.config import IMG_PATH
from view.Dialog import CreateVenvDialog
from view.DockTitleBar import DockTitleBar
from view.Editor import Editor


class CodeWindow(QMainWindow):
    """
    代码窗口实现类
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.dock_show = False
        self.syntax_error = None
        self.init_ui()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

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
        self.layout = QVBoxLayout(self)

        self.stacked_widget = QStackedWidget()

        self.info_widget = TextEdit(self.stacked_widget)
        self.info_widget.setReadOnly(True)
        self.info_widget.setStyleSheet("background-color: rgba(0, 0, 0,0)")
        self.info_widget.setTextColor(QColor('black'))

        self.log_widget = TextEdit(self.stacked_widget)
        self.log_widget.setStyleSheet("background-color: rgba(0, 0, 0,0)")
        self.log_widget.setReadOnly(True)

        self.stacked_widget.addWidget(self.info_widget)
        self.stacked_widget.addWidget(self.log_widget)

        self.infoDock = QDockWidget("Info Dock", self)
        self.infoDock.setWidget(self.stacked_widget)
        self.infoDock.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #f0f0f0;
            border-radius: 7px;
        """)
        self.interpreter_list = QListWidget()

        self.dock_title = DockTitleBar(self.infoDock)
        self.dock_title.setMinBtn(self.dock_hide)
        self.infoDock.setTitleBarWidget(self.dock_title)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.infoDock)

        self.infoDock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable |
                                  QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.infoDock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.infoDock.hide()

        # 创建状态栏按钮
        self.toggleButton = self.create_status_button('syntax_info.png', self.switch_widget, 0)
        self.show_log_button = self.create_status_button('code_run.png', self.switch_widget, 1)
        self.dock_btn = QPushButton("解释器管理", self)
        self.dock_btn.setCheckable(True)
        self.dock_btn.setChecked(True)
        self.dock_btn.setStyleSheet(ButtonStyleSheet)
        self.dock_btn.clicked.connect(self.show_dock_menu)

        self.__statusBar = self.statusBar()
        self.__statusBar.addPermanentWidget(self.toggleButton)
        self.__statusBar.addPermanentWidget(self.show_log_button)
        self.__statusBar.addPermanentWidget(self.dock_btn)
        self.__statusBar.setFixedHeight(24)

        self.__changeTimer = QTimer()
        self.__changeTimer.timeout.connect(self.check_syntax)
        self.__changeTimer.start(5000)

    def show_dock_menu(self):
        menu = QMenu()
        history_action = menu.addAction("解释器列表")
        history_action.triggered.connect(self.show_history)
        create_action = menu.addAction("创建解释器")
        create_action.triggered.connect(self.show_create_venv_dialog)
        delete_action = menu.addAction("删除解释器")
        delete_action.triggered.connect(self.delete_virtual_environment)
        menu.exec(self.dock_btn.mapToGlobal(self.dock_btn.rect().bottomLeft()))

    def show_history(self):
        menu = QMenu()
        for index in range(self.interpreter_list.count()):
            interpreter = self.interpreter_list.item(index).text()
            action = menu.addAction(interpreter)
            action.triggered.connect(lambda checked, interp=interpreter: self.set_default_interpreter(interp))
        menu.exec(self.dock_btn.mapToGlobal(self.dock_btn.rect().bottomLeft()))

    def show_create_venv_dialog(self):
        main_window_rect = self.parent.parent.geometry()
        dialog = CreateVenvDialog(self)
        dialog_rect = dialog.geometry()
        center_x = main_window_rect.x() + (main_window_rect.width() - dialog_rect.width()) // 3
        center_y = main_window_rect.y() + (main_window_rect.height() - dialog_rect.height()) // 3

        dialog.move(center_x, center_y)

        dialog.exec()

    def delete_virtual_environment(self):
        selected_item = self.interpreter_list.currentItem()
        if selected_item:
            interpreter_path = selected_item.text()
            confirm = QMessageBox.question(self, "Confirm Delete",
                                           f"Are you sure you want to delete {interpreter_path}?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.interpreter_list.takeItem(self.interpreter_list.row(selected_item))
                if interpreter_path == self.dock_btn.text():
                    self.dock_btn.setChecked('解释器管理')

    def add_interpreter(self, interpreter_path):
        if interpreter_path:
            self.add_interpreter_to_history(interpreter_path)

    def add_interpreter_to_history(self, interpreter_path):
        if not any(
                self.interpreter_list.item(i).text() == interpreter_path for i in range(self.interpreter_list.count())):
            self.interpreter_list.addItem(interpreter_path)

    def set_default_interpreter(self, interpreter_path=None):
        if interpreter_path is None:
            selected_item = self.interpreter_list.currentItem()
            if selected_item:
                interpreter_path = selected_item.text()
        if interpreter_path:
            self.dock_btn.setText(interpreter_path)

    def remove_interpreter(self):
        selected_item = self.interpreter_list.currentItem()
        if selected_item:
            self.interpreter_list.takeItem(self.interpreter_list.row(selected_item))
            if self.dock_btn.text() == selected_item.text():
                self.dock_btn.setText('解释器管理')

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
        self.tabs.addTab(editor, file_path.split('/')[-1])
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
