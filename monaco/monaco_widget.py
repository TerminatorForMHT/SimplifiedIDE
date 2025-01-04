import json
from pathlib import Path

from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot, pyqtProperty
from PyQt6.QtWebEngineCore import QWebEnginePage
from qframelesswindow.webengine import FramelessWebEngineView


class BaseBridge(QObject):
    initialized = pyqtSignal()
    sendDataChanged = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.active = False
        self.queue = []

    def send_to_js(self, name, value):
        if self.active:
            data = json.dumps(value)
            self.sendDataChanged.emit(name, data)
        else:
            self.queue.append((name, value))

    @pyqtSlot(str, str)
    def receive_from_js(self, name, value):
        data = json.loads(value)
        self.setProperty(name, data)

    @pyqtSlot()
    def init(self):
        self.initialized.emit()
        self.active = True
        for name, value in self.queue:
            self.send_to_js(name, value)
        self.queue.clear()


class EditorBridge(BaseBridge):
    valueChanged = pyqtSignal()
    languageChanged = pyqtSignal()
    themeChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._value = ''
        self._language = ''
        self._theme = ''

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.valueChanged.emit()

    def getLanguage(self):
        return self._language

    def setLanguage(self, language):
        self._language = language
        self.languageChanged.emit()

    def getTheme(self):
        return self._theme

    def setTheme(self, theme):
        self._theme = theme
        self.themeChanged.emit()

    value = pyqtProperty(str, fget=getValue, fset=setValue, notify=valueChanged)
    language = pyqtProperty(str, fget=getLanguage, fset=setLanguage, notify=languageChanged)
    theme = pyqtProperty(str, fget=getTheme, fset=setTheme, notify=themeChanged)


index = Path(__file__).parent / 'index.html'

with open(index) as f:
    raw_html = f.read()


class MonacoPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        pass


class MonacoWidget(FramelessWebEngineView):
    initialized = pyqtSignal()
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        page = MonacoPage(parent=self)
        self.setPage(page)

        filename = Path(__file__).parent / 'index.html'
        self.setHtml(raw_html, QUrl.fromLocalFile(filename.as_posix()))

        self._channel = QWebChannel(self)
        self._bridge = EditorBridge()

        self.page().setWebChannel(self._channel)
        self._channel.registerObject('bridge', self._bridge)

        self._bridge.initialized.connect(self.initialized)
        self._bridge.valueChanged.connect(lambda: self.textChanged.emit(self._bridge.value))

    def text(self):
        return self._bridge.value

    def setText(self, text):
        self._bridge.send_to_js('value', text)

    def language(self):
        return self._bridge.language

    def setLanguage(self, language):
        self._bridge.send_to_js('language', language)

    def theme(self):
        return self._bridge.theme

    def setTheme(self, theme):
        self._bridge.send_to_js('theme', theme)

    def setEditorOptions(self, options):
        """设置编辑器选项"""
        self._bridge.send_to_js('setEditorOptions', options)

    def executeEditorCommand(self, command):
        """执行编辑器命令"""
        self._bridge.send_to_js('executeEditorCommand', command)

    def registerLanguage(self, language_id, definition):
        """注册语言"""
        self._bridge.send_to_js('registerLanguage', {'id': language_id, 'definition': definition})

    def registerTheme(self, theme_name, definition):
        """注册主题"""
        self._bridge.send_to_js('registerTheme', {'themeName': theme_name, 'definition': definition})

    def addEventListener(self, event_name):
        """添加事件监听"""
        self._bridge.send_to_js('addEventListener', event_name)
