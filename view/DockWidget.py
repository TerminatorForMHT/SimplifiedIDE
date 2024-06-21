from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget, QWidget, QSizePolicy
from qfluentwidgets import TextEdit
from view.DockTitleBar import DockTitleBar


class DockWidget(QWidget):
    hide_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dock_show = False
        self.init_ui()

    def init_ui(self):
        self.setLayout(QVBoxLayout(self))
        self.dock_title = DockTitleBar(self)
        self.dock_title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.dock_title.setMinBtn(self.hide)

        self.layout().addWidget(self.dock_title)

        self.stacked_widget = QStackedWidget()
        self.layout().addWidget(self.stacked_widget)

        self.info_widget = TextEdit(self)
        self.log_widget = TextEdit(self)

        self.stacked_widget.addWidget(self.info_widget)
        self.stacked_widget.addWidget(self.log_widget)

    def switch_widget(self, index):
        if self.dock_show and self.stacked_widget.currentIndex() == index:
            self.hide()
        else:
            self.stacked_widget.setCurrentIndex(index)
            self.show()

    def hide(self):
        self.stacked_widget.hide()
        self.dock_title.hide()
        self.dock_show = False
        self.hide_signal.emit()

    def show(self):
        self.stacked_widget.show()
        self.dock_title.show()
        self.dock_show = True
