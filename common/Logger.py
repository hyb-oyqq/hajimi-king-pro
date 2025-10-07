import logging
import traceback
import os
from datetime import datetime
from pathlib import Path

# 创建日志目录
def get_log_dir():
    """获取日志目录路径"""
    data_path = os.getenv('DATA_PATH', 'data')
    log_dir = Path(data_path) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

# 配置日志
log_dir = get_log_dir()
log_file = log_dir / f"hajimi_king_pro_{datetime.now().strftime('%Y%m%d')}.log"

# 创建格式化器
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

# 创建文件处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)


class Logger:
    @staticmethod
    def info(message):
        logging.info(str(message))

    @staticmethod
    def warning(message):
        # 控制台显示颜色，文件不显示
        msg = str(message)
        # 记录到文件（无颜色）
        logging.warning(msg)

    @staticmethod
    def error(message, exc_info=False):
        """
        记录错误信息
        
        Args:
            message: 错误消息
            exc_info: 是否包含异常堆栈信息
        """
        msg = "-" * 50 + '\n| ' + str(message)
        
        # 如果需要包含异常信息，添加堆栈跟踪
        if exc_info:
            msg += "\n" + traceback.format_exc()
        
        msg += "\n" + "└" + "-" * 70
        
        # 记录到文件（无颜色）
        logging.error(msg)

    @staticmethod
    def debug(message):
        logging.debug(str(message))


logger = Logger()
