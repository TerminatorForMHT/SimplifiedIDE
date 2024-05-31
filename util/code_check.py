import json
import logging
from pylint.lint import Run
from pylint.reporters.json_reporter import JSONReporter
from io import StringIO

from util.config import PYLINTRC_PATH


def run_pylint_on_code(path):
    try:
        # 使用StringIO捕获Pylint的JSON输出
        pylint_output = StringIO()
        reporter = JSONReporter(output=pylint_output)

        # 捕获系统退出异常
        try:
            options = [f'--rcfile={PYLINTRC_PATH}', path]
            Run(options, reporter=reporter)
        except SystemExit as e:
            if e.code != 0 and e.code != 20:
                logging.warning(f'An exception occurred during the pylint syntax check, please check')

        # 解析JSON输出
        pylint_output.seek(0)
        ret = json.loads(pylint_output.getvalue())
        return ret
    finally:
        logging.info('Pylint Run Ends')
