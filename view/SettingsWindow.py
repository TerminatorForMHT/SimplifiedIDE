from qfluentwidgets import MSFluentWindow


class SettingsWindow(MSFluentWindow):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("设置")
        self.env_manager = None
