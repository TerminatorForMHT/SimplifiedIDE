import platform


def isMacOS() -> bool:
    """
    判断运行环境是否是MacOS
    :return:
    """
    return platform.system() == 'Darwin'
