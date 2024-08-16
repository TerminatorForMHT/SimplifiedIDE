from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit


class InputDialog(MessageBoxBase):

    def __init__(self, title_text, placeholer_text, parent=None):
        super().__init__(parent=parent)

        self.titleLabel = SubtitleLabel(title_text)
        self.urlLineEdit = LineEdit()

        self.urlLineEdit.setPlaceholderText(placeholer_text)
        self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)

        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)
