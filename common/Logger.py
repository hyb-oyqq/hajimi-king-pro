import logging
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')


class Logger:
    @staticmethod
    def info(message):
        logging.info(str(message))

    @staticmethod
    def warning(message):
        logging.warning("\033[0;33m" + str(message) + "\033[0m")

    @staticmethod
    def error(message, exc_info=False):
        """
        记录错误信息
        
        Args:
            message: 错误消息
            exc_info: 是否包含异常堆栈信息
        """
        error_msg = "\033[0;31m" + "-" * 50 + '\n| ' + str(message) + "\033[0m"
        
        # 如果需要包含异常信息，添加堆栈跟踪
        if exc_info:
            error_msg += "\n" + traceback.format_exc()
        
        error_msg += "\n" + "└" + "-" * 70
        logging.error(error_msg)

    @staticmethod
    def debug(message):
        logging.debug("\033[0;37m" + str(message) + "\033[0m")


logger = Logger()
