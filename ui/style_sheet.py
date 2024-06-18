CodeTabStyleSheet = """
            QTabWidget {
                border: 0px solid rgb(0, 0, 0);
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                text-align: left;
                border: 1px solid rgb(0, 0, 0);
                border-radius: 0px; 
            }
            QTabBar::tab:hover{
                background-color: rgb(72, 140, 245);
                color: rgb(255, 255, 255);
            }
            QTabBar::tab:selected {
                background-color: rgb(0, 0, 255);
                color: rgb(255, 255, 255);
            }
            """
CodeWindowStyleSheet = """
        QMainWindow {
            border: 0px solid #1B1D23;
        }
        """
CodeEditorStyleSheet = """
        QsciScintilla {
            border: 1px solid #1B1D23;
            border-radius: 7px; 
            background-color: palette(window);
        }
        """
CodeLabelStyleSheet = """
        QLabel{
            font-size: 13px;
            color: black;
            background-color: palette(window);
            border: 1px solid black;
            padding: 10px;
        }
"""

ButtonStyleSheet = """
    QPushButton{
        background-color: rgba(255, 255, 255, 0);
        border: 0px;
    }
    QPushButton:hover {
        background-color: rgb(72, 140, 245);
    }
"""

ExitButtonStyleSheet = """
    QPushButton{
        background-color: rgba(255, 255, 255, 0);
        border: 0px;
    }
    QPushButton:hover {
        background-color: rgb(255, 0, 0);
    }
"""

TreeStyleSheetForMac = """
     QTreeView {
        border-radius: 7px;
        background-color: palette(window);
    }
"""
TreeStyleSheet = """
     QTreeView {
        border-radius: 7px;
}
"""
StatusBarStyleSheet = """
    QStatusBar {
        background-color: palette(window);
    }
"""
