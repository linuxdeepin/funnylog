from simplelog import logger
from simplelog import log

@log
class TestWidget:

    def dosometing(self):
        """let do something"""

if __name__ == '__main__':
    logger("DEBUG")
    logger.info("this is info log")
    # TestWidget().dosometing()