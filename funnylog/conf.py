import os
from getpass import getuser
from platform import machine


class _Setting:

    SYS_ARCH = machine()
    USERNAME = getuser()
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 日志文件生成的路径
    LOG_PATH = os.path.join(ROOT_DIR, "logs")
    # 本机IP
    HOST_IP = str(os.popen("hostname -I |awk '{print $1}'").read()).strip("\n").strip()

    LOG_LEVEL = "DEBUG"
    CLASS_NAME_STARTSWITH = ()
    CLASS_NAME_ENDSWITH = ()
    CLASS_NAME_CONTAIN = ()

setting = _Setting()