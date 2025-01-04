var bridge = null;
var editor = null;

require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });
require(['vs/editor/editor.main'], () => {
    const container = document.getElementById('container');
    editor = monaco.editor.create(container, {
        fontFamily: "Monaco",
        automaticLayout: true,
    });

    // 内容更改事件
    editor.onDidChangeModelContent(() => {
        sendToPython("value", editor.getModel().getValue());
    });

    // 语言更改事件
    editor.onDidChangeModelLanguage((event) => {
        sendToPython("language", event.newLanguage);
    });

    // 禁用 Ctrl + 鼠标左键单击事件监控
    editor.onMouseDown((event) => {
        if (event.event.ctrlKey && event.target.type === monaco.editor.MouseTargetType.CONTENT_TEXT) {
            event.event.preventDefault();
        }
    });
});

/**
 * 初始化编辑器的状态并发送到 Python
 */
function init() {
    sendToPython("value", editor.getModel().getValue());
    sendToPython("language", editor.getModel().getLanguageId());
    sendToPython("theme", editor._themeService._theme.themeName);
}

/**
 * 发送数据到 Python
 * @param {string} name 数据名称
 * @param {string} value 数据值
 */
function sendToPython(name, value) {
    bridge.receive_from_js(name, JSON.stringify(value));
}

/**
 * 从 Python 更新编辑器状态
 * @param {string} name 数据名称
 * @param {string} value 数据值
 */
function updateFromPython(name, value) {
    const data = JSON.parse(value);
    switch (name) {
        case "value":
            editor.getModel().setValue(data);
            break;
        case "language":
            monaco.editor.setModelLanguage(editor.getModel(), data);
            break;
        case "theme":
            monaco.editor.setTheme(data);
            sendToPython("theme", editor._themeService._theme.themeName);
            break;
    }
}

/**
 * 更新编辑器选项
 * @param {object} options 配置选项
 */
function setEditorOptions(options) {
    editor.updateOptions(options);
}

/**
 * 执行编辑器命令
 * @param {string} command 命令名称
 */
function executeEditorCommand(command) {
    editor.trigger(null, command, null);
}

/**
 * 注册自定义语言
 * @param {string} languageId 语言标识符
 * @param {object} definition 语言定义
 */
function registerLanguage(languageId, definition) {
    monaco.languages.register({ id: languageId });
    monaco.languages.setMonarchTokensProvider(languageId, definition);
}

/**
 * 注册自定义主题
 * @param {string} themeName 主题名称
 * @param {object} definition 主题定义
 */
function registerTheme(themeName, definition) {
    monaco.editor.defineTheme(themeName, definition);
}

/**
 * 添加编辑器事件监听
 * @param {string} eventName 事件名称
 */
function addEventListener(eventName) {
    switch (eventName) {
        case "contentChanged":
            editor.onDidChangeModelContent(() => {
                const content = editor.getValue();
                sendToPython("contentChanged", content);
            });
            break;
        case "cursorPositionChanged":
            editor.onDidChangeCursorPosition(() => {
                const position = editor.getPosition();
                sendToPython("cursorPositionChanged", position);
            });
            break;
        default:
            console.error(`Unknown event: ${eventName}`);
    }
}

/**
 * 页面加载完成后初始化桥接
 */
window.onload = function () {
    // 初始化 QWebChannel
    new QWebChannel(qt.webChannelTransport, function (channel) {
        bridge = channel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();
        init();
    });
};