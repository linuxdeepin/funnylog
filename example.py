from funnylog import logger
from funnylog import log
from funnylog.conf import setting


class BaseLog:

    def base_self_method(self):
        """我是基类里面的实例方法"""

    @classmethod
    def base_cls_method(self):
        """我是基类里面的类方法"""

    @staticmethod
    def base_static_method(self):
        """我是基类里面的静态方法"""


@log
class TestLog(BaseLog):

    def self_method(self):
        """我是类里面的实例方法"""

    @classmethod
    def cls_method(self):
        """我是类里面的类方法"""

    @staticmethod
    def static_method(self):
        """我是类里面的静态方法"""


if __name__ == '__main__':
    logger("DEBUG")
    # logger.debug("这是 debug log")
    # logger.info("这是 info log")
    # logger.error("这是 is error log")

    setting.CLASS_NAME_ENDSWITH = ("Log",)

    test = TestLog()
    test.self_method()
