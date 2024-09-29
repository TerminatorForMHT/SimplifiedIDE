import os
import platform
import sys

if __name__ == '__main__':
    env_path = os.path.dirname(sys.executable)
    pack_path = os.path.dirname(__file__)
    system_type = platform.system()

    print('编译开始'.center(80, '='))

    if system_type == "Windows":
        command = f'{env_path}/pyinstaller {pack_path}/OnWindows.spec'.replace('/', os.sep)
        os.system(command)
    elif system_type == "Darwin":
        command = f'{env_path}/pyinstaller {pack_path}/OnMac.spec'.replace('/', os.sep)
        os.system(command)

    print('编译结束'.center(80, '='))
    print(f'编译文件存放在{pack_path}/dist/Wally')
