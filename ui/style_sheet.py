CodeTabStyleSheet = """
        QTabWidget::pane {
            background-color: rgba(255, 255, 255, 0);
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }

        QTabBar::tab {
            text-align: left;
            background: #e1e1e1;
            border: 1px solid #ccc;
            padding: 5px;
            color: #333;
        }

        QTabBar::tab:selected {
            background: #ffffff;
            color: #000;
            border-bottom: 2px solid #0078d7;
        }

        QTabBar::tab:hover {
            background: #f0f0f0;
        }

        QTabBar::tab:!selected {
            margin-top: 2px;
        }

        QTabBar::tab:only-one {
            margin: 0;
        }
        
        QTabBar::close-button {
            subcontrol-position: right;
        }

        QTabBar::close-button:hover {
            background: #e81123;
            border-radius: 3px;
        }

        QTabBar::close-button:pressed {
            background: #c50f1f;
            border-radius: 3px;
        }
"""
CodeWindowStyleSheet = """
        QMainWindow {
            background-color: rgba(255, 255, 255, 0);
        }
        """
CodeEditorStyleSheet = """
        QsciScintilla {
           background-color: rgba(255, 255, 255, 0);
        }
        QsciScintilla::viewport {
            background-color: rgba(255, 255, 255, 0);
        }
        """
CodeLabelStyleSheet = """
        QLabel{
            font-size: 13px;
            color: black;
            background-color: rgba(255, 255, 255, 0);
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

TreeStyleSheet = """
     QTreeView {
        border-radius: 7px;
}
"""
StatusBarStyleSheet = """
    QStatusBar {
        background-color: rgba(255, 255, 255, 0);
    }
"""
