import os
import sys
from pathlib import Path

from PyQt6.QtCore import QSettings

LOAD_FILE_TYPE = 'Python Files (*.py);;Python Interface Files (*.pyi);;Text Files (*.txt)'

ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent
IMG_PATH = ROOT_PATH / 'src' / 'static' / 'img'
PYLINTRC_PATH = ROOT_PATH / 'src' / 'pylint' / 'pylintrc'

MySettings = QSettings("LastProject", "PythonPad++")

NotMac = sys.platform != 'darwin'

SEP = '\\' if sys.platform == "win32" else '/'
