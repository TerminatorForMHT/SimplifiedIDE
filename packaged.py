import os
import shutil
import sys

env_path = os.path.dirname(sys.executable)
build_path=f"{os.path.dirname(__file__)}/build"


if __name__ == '__main__':
    command = f'{env_path}/pyinstaller Notepad.spec'.replace('/', os.sep)
    os.system(command)
    shutil.rmtree(build_path)
