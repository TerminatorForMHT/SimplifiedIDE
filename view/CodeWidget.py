import os
from pathlib import PurePath

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from qfluentwidgets import TabBar, RoundMenu, Action

from util.config import IMG_PATH
from view.Editor import Editor


class CodeWidget(QWidget):
    open_file_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.tab_bar = TabBar()
        self.tab_bar.setAddButtonVisible(False)
        self.stacked_widget = QStackedWidget()

        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.stacked_widget)

        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.tabBarClicked.connect(self.switch_tab)

    def load_file(self, file_path):
        self.add_new_tab(file_path)

    def add_new_tab(self, file_path):
        editor = Editor(self)
        editor.load_file(file_path)
        editor.ctrl_left_click_signal.connect(self.handle_ctrl_left_click)
        self.stacked_widget.addWidget(editor)

        index = self.stacked_widget.count() - 1
        self.tab_bar.addTab(index, file_path.split('/')[-1])
        self.tab_bar.setCurrentTab(index)
        self.stacked_widget.setCurrentWidget(editor)
        return editor

    def close_tab(self, index):
        if self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(index)
            widget.deleteLater()
            self.stacked_widget.removeWidget(widget)
            self.tab_bar.removeTab(index)

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def jump_to_assign_tab(self, file_path, line, index):
        editor = self.add_new_tab(file_path)
        editor.move_cursor_visible(line, index)

    def jump_to_assign_line(self, line, index):
        self.stacked_widget.currentWidget().move_cursor_visible(line, index)

    def reference_jump(self, jump_info: dict):
        path, line, column = jump_info['ModulePath'], jump_info['Line'], jump_info['Column']
        self.jump_to_assign_tab(path, line, column)

    def show_reference_menu(self, reference_addr):
        menu = RoundMenu()
        icon = str(IMG_PATH.joinpath(PurePath('python.png')))
        for item in reference_addr:
            file = item['ModulePath'].split(os.sep)[-1]
            line, code = item['Line'], item['Code']
            item_info = f'{file}    {line}   {code}'
            menu.addAction(Action(QIcon(icon), item_info, triggered=lambda item=item: self.reference_jump(item)))
        menu.exec(QCursor.pos())

    def handle_ctrl_left_click(self, info: dict):
        assign_addr = info.get("assign_addr")
        reference_addr = info.get("reference_addr")

        if assign_addr:
            path, line, index = assign_addr['ModulePath'], assign_addr['Line'], assign_addr['Column']
            current_tab = self.stacked_widget.currentWidget()
            if path != current_tab.current_file_path:
                self.jump_to_assign_tab(path, line, index)
            else:
                self.jump_to_assign_line(line, index)
        elif reference_addr:
            self.show_reference_menu(reference_addr)
