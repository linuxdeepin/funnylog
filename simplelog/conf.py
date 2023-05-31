import os
from getpass import getuser
from platform import machine


class _Setting:

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    REPORT_PATH = os.path.join(ROOT_DIR, "logs")
    HOST_IP = str(os.popen("hostname -I |awk '{print $1}'").read()).strip("\n").strip()
    SYS_ARCH = machine()
    USERNAME = getuser()

setting = _Setting()