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
            border: 1px solid #1B1D23;
        }
        """
CodeEditorStyleSheet = """
        QsciScintilla {
            border: 1px solid #1B1D23;
            border-radius: 7px; 
        }
        """
CodeLabelStyleSheet = """
        QLabel{
            font-size: 13px;
            color: black;
            background-color: rgb(255, 255, 255);
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
        background-color: rgb(255, 255, 255);
    }
"""
