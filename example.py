from funnylog import logger
from funnylog import log
from funnylog.conf import setting

@log
class TestLog:

    def dosometing(self):
        """我是函数功能说明，我能自动打印"""
        print("我是print")

if __name__ == '__main__':
    logger("DEBUG")
    logger.debug("this is debug log")
    logger.info("this is info log")
    logger.error("this is error log")

    setting.CLASS_NAME_ENDSWITH = ("Log",)
    TestLog().dosometing()