# coding:utf-8
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from qframelesswindow.titlebar import MinimizeButton

from ui.style_sheet import ButtonStyleSheet


class DockTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn = MinimizeButton(parent=self)
        self.minBtn.setStyleSheet(ButtonStyleSheet)
        # self.resize(200, 20)
        self.setFixedHeight(20)
        self.window().installEventFilter(self)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(20, 0, 20, 0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.minBtn, 0, Qt.AlignmentFlag.AlignRight)

    def setMinBtn(self, func):
        self.minBtn.clicked.connect(func)
