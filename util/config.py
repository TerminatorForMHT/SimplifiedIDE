import os
from pathlib import Path

LoadFileType = 'Python Files (*.py);;Python Interface Files (*.pyi);;Text Files (*.txt)'

ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent
IMG_PATH = ROOT_PATH / 'src' / 'static' / 'img'
PYLINTRC_PATH = ROOT_PATH / 'src' / 'pylint' / 'pylintrc'