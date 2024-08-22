import logging
import subprocess
import sys
import io

from conf.config import MySettings

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PythonExecutor:
    def __init__(self):
        self.returncode = None
        self.stderr = None
        self.stdout = None
        self.log_capture_string = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture_string)
        self.handler.setLevel(logging.INFO)
        logger.addHandler(self.handler)

    def execute_file(self, file_path: str):
        interpreter_path = MySettings.value("default_interpreter")
        try:
            # 使用指定的 Python 解释器执行文件
            result = subprocess.run([interpreter_path, file_path], text=True, capture_output=True)

            # 记录标准输出和标准错误
            if result.stdout:
                self.stdout = result.stdout
            if result.stderr:
                self.stderr = result.stderr
            self.returncode = result.returncode
        except Exception as e:
            logger.error(f"执行文件时出错: {e}")

        logger.info("文件执行完毕")

    def get_logs(self):
        # 返回日志内容
        return self.log_capture_string.getvalue()
