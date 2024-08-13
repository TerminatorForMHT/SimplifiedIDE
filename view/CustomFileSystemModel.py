from pathlib import PurePath

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFileSystemModel

from conf.config import IMG_PATH
from util.suffixMap2name import suffixMap


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DecorationRole:
            file_path = self.filePath(index)
            if "." in file_path:
                if 'requirements.txt' in str(file_path).lower():
                    return QIcon(str(IMG_PATH.joinpath(PurePath('Requirements.svg'))))
                suffix = file_path.split(".")[-1]
                icon_name = suffixMap.get(suffix)
                if icon_name:
                    return QIcon(str(IMG_PATH.joinpath(PurePath(f'{icon_name}.svg'))))
            elif 'license' in str(file_path).lower():
                return QIcon(str(IMG_PATH.joinpath(PurePath('License.svg'))))
        return super().data(index, role)
