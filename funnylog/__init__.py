import inspect
import logging
import os
import re
import sys
import threading
import time
import weakref
from functools import wraps
from inspect import _ParameterKind

try:
    from allure_commons._allure import StepContext
    from allure_commons.utils import func_parameters, represent

    ALLURE_STEP = True
except ModuleNotFoundError:
    ALLURE_STEP = False

from funnylog.conf import setting


class Singleton(type):
    """单例模式"""

    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Singleton.__instance = None
        # 初始化存放实例地址
        self._cache = weakref.WeakValueDictionary()

    def __call__(self, *args, **kwargs):
        # 提取类初始化时的参数
        kargs = "".join([f"{key}" for key in args]) if args else ""
        kkwargs = "".join([f"{key}" for key in kwargs]) if kwargs else ""
        # 判断相同参数的实例师否被创建
        if kargs + kkwargs not in self._cache:  # 存在则从内存地址中取实例
            with Singleton._instance_lock:
                Singleton.__instance = super().__call__(*args, **kwargs)
                self._cache[kargs + kkwargs] = Singleton.__instance
        # 不存在则新建实例
        else:
            Singleton.__instance = self._cache[kargs + kkwargs]
        return Singleton.__instance


def is_static_method(klass_or_instance, attr: str):
    """Test if a value of a class is static method.
    example::
        class MyClass(object):
            @staticmethod
            def add_two(a, b):
                return a + b
    :param klass_or_instance: the class
    :param attr: attribute name
    """
    if attr.startswith("_"):
        return False
    value = getattr(klass_or_instance, attr)
    # is a function or method
    if inspect.isroutine(value):
        if isinstance(value, property):
            return False
        args = []
        for param in inspect.signature(value).parameters.values():
            kind = param.kind
            name = param.name
            if kind is _ParameterKind.POSITIONAL_ONLY:
                args.append(name)
            elif kind is _ParameterKind.POSITIONAL_OR_KEYWORD:
                args.append(name)
        # Can't be a regular method, must be a static method
        if len(args) == 0:
            return True
        # must be a regular method
        if args[0] == "self":
            return False
        return inspect.isfunction(value)
    return False


def _trace(func):
    # pylint: disable=R0912
    @wraps(func)
    def wrapped(*a, **kw):
        try:
            # 对象实例化后调用类方法报错处理
            if (
                    # pylint: disable=protected-access
                    isinstance(a[0], inspect._findclass(func))
                    and func.__name__ != "__init__"
            ):
                if func:
                    if any(
                            [
                                inspect.ismethod(func),
                                is_static_method(
                                    # pylint: disable=protected-access
                                    inspect._findclass(func),
                                    func.__name__,
                                ),
                            ]
                    ):
                        a = list(a)[1:]
        except IndexError:
            pass
        params = func_parameters(func, *a, **kw)
        # pylint: disable=unnecessary-lambda
        args = list(map(lambda x: represent(x), a))
        if func.__doc__:
            if not func.__name__.startswith("_"):
                # 处理多行注释时候，换行空格过多
                title = re.split(":param|@param|@return|:return", func.__doc__)[0]
                title = "".join([ln.strip() for ln in title.split("\n")])
                params_text = {}
                # 获取方法的所有参数，并行程，{形参：实参} 的字典
                for index, param in enumerate(
                        inspect.signature(func).parameters.values()
                ):
                    if param.name == "self":
                        continue
                    params_text[param.name] = param.default
                    if args:
                        try:
                            params_text[param.name] = args[index]
                        except IndexError:
                            pass
                    if kw:
                        try:
                            params_text[param.name] = kw[param.name]
                        except KeyError:
                            pass
                # 文本替换
                for parameter, argument in params_text.items():
                    if f"{parameter}" in title:
                        if argument:
                            title = title.replace(
                                f"{{{{{parameter}}}}}",
                                argument.strip("'")
                                if isinstance(argument, str)
                                else str(argument),
                            )
                        else:
                            title = title.replace(f"{{{{{parameter}}}}}", "")
            else:
                return func(*a, **kw)
        else:
            title = func.__name__
        logger.info(f"[{func.__name__}]: " f"{title}", auteadd=False)
        if func.__name__ != "__init__":
            with StepContext(title, params):
                return func(*a, **kw)
        else:
            return func(*a, **kw)

    return wrapped


def log(cls):
    """
    类日志装饰器
    :param cls:
    :return:
    """
    for name, obj in inspect.getmembers(
            cls, lambda x: inspect.isfunction(x) or inspect.ismethod(x)
    ):
        try:
            class_name = obj.__qualname__.split(".")[0]
        except AttributeError:
            class_name = obj.__self__.__name__
        if name.startswith("_"):
            continue
        # else:
        if (
                class_name.startswith(setting.CLASS_NAME_STARTSWITH)
                or class_name.endswith(setting.CLASS_NAME_ENDSWITH)
                or any(
            (class_name.find(text) > -1 for text in setting.CLASS_NAME_CONTAIN)
        )
        ):
            if hasattr(getattr(cls, name), "__log"):
                if not getattr(cls, name).__log:
                    setattr(cls, name, _trace(obj))
                    setattr(getattr(cls, name), "__log", True)
            else:
                setattr(cls, name, _trace(obj))
                setattr(getattr(cls, name), "__log", True)
    return cls


class _ColoredFormatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        """Format a message from a record object."""
        if record.levelname == "INFO":
            record.levelname = "\033[1;97mINFO \033[0m"  # 白色
            record.message = re.sub(
                r"(\[[a-zA-Z_]*?])?(.+)",
                r"\033[1;32m\1\033[0m\033[1;97m\2\033[0m",
                record.message,
                count=1,
            )
            # record.message = f"\033[1;97m{record.message}\033[0m"
        elif record.levelname == "ERROR":
            record.levelname = "\033[1;31mERROR\033[0m"  # 红色
            # record.message = f"\033[1;31m{record.message}\033[0m"
            record.message = re.sub(
                r"(\[[a-zA-Z_]*?])?(.+)",
                r"\033[1;32m\1\033[0m\033[1;31m\2\033[0m",
                record.message,
                count=1,
            )
        elif record.levelname == "DEBUG":
            record.levelname = "\033[1;94mDEBUG\033[0m"  # 蓝色
            record.message = re.sub(
                r"(\[[a-zA-Z_]*?])?(.+)",
                r"\033[1;32m\1\033[0m\033[1;94m\2\033[0m",
                record.message,
                count=1,
            )
        message = super().formatMessage(record)
        return message


# pylint: disable=R0903
class IgnoreFilter(logging.Filter):
    """IgnoreFilter"""

    def filter(self, record):
        return record.name not in ("PIL.PngImagePlugin", "easyprocess")


# pylint: disable=invalid-name
class logger(metaclass=Singleton):
    """logger"""
    __author__ = "Litao <litaoa@uniontech.com>"

    def __init__(self, level):
        """
        日志配置
        :param level: case 路径
        """
        # 清空其他日志配置
        logging.root.handlers = []
        log_path = os.path.join(setting.LOG_PATH, "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_path_debug = (
                log_path + rf'/{time.strftime("%Y-%m-%d", time.localtime())}_debug.log'
        )  # debug级别日志路径
        logfile_error = (
                log_path + rf'/{time.strftime("%Y-%m-%d", time.localtime())}_error.log'
        )  # error级别日志路径
        # 路径不存在则创建
        if os.path.exists(log_path_debug):
            with open(log_path_debug, "w+", encoding="utf-8"):
                pass
        if os.path.exists(logfile_error):
            with open(logfile_error, "w+", encoding="utf-8"):
                pass
        try:
            self.ip_end = re.findall(r"\d+.\d+.\d+.(\d+)", f"{setting.HOST_IP}")[0]
            self.ip_flag = f"-{self.ip_end}"
        except IndexError:
            self.ip_flag = ""
        self.sys_arch = (
            setting.SYS_ARCH[:7] + "*"
            if len(setting.SYS_ARCH) > 6
            else setting.SYS_ARCH
        )
        self.user_name = (
            setting.USERNAME[:7] + "*"
            if len(setting.USERNAME) > 6
            else setting.USERNAME
        )
        self.date_format = "%m/%d %H:%M:%S"
        self.log_format = (
            f"{self.sys_arch}-{self.user_name}{self.ip_flag}: "
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        self.logger = logging.getLogger()
        self.logger.setLevel(level)  # Log等级总开关
        self.logger.addFilter(IgnoreFilter())
        _fh = logging.FileHandler(log_path_debug, mode="w+")
        _fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        _fh.addFilter(IgnoreFilter())
        _fh.setFormatter(
            logging.Formatter(
                self.log_format,
                datefmt=self.date_format,
            )
        )
        fh_error = logging.FileHandler(logfile_error, mode="w+")
        _fh.setFormatter(
            logging.Formatter(
                self.log_format,
                datefmt=self.date_format,
            )
        )
        fh_error.setLevel(logging.ERROR)  # 输出到file的log等级的开关
        # 第四步，再创建一个handler，用于输出到控制台
        _ch = logging.StreamHandler()
        _ch.setLevel(level)  # 输出到console的log等级的开关
        _ch.addFilter(IgnoreFilter())
        # 第五步，定义handler的输出格式
        formatter = _ColoredFormatter(
            (
                f"\033[1;31m{self.sys_arch}-{self.user_name}{self.ip_flag}\033[0m: "
                "\033[93m%(asctime)s\033[0m | %(levelname)s | %(message)s"
            ),
            datefmt=self.date_format,
        )
        _ch.setFormatter(formatter)
        # 第六步，将logger添加到handler里面
        self.logger.addHandler(_fh)
        self.logger.addHandler(fh_error)
        self.logger.addHandler(_ch)

    @staticmethod
    def info(message, auteadd=True):
        """info"""
        if len(logging.root.handlers) == 0:
            logger(setting.LOG_LEVEL)
        if auteadd:
            current_frame = sys._getframe(1) if hasattr(sys, "_getframe") else None
            message = f"[{current_frame.f_code.co_name}]: {message}"
        logging.info(message)

    @staticmethod
    def debug(message, auteadd=True):
        """debug"""
        if len(logging.root.handlers) == 0:
            logger(setting.LOG_LEVEL)
        if auteadd:
            current_frame = sys._getframe(1) if hasattr(sys, "_getframe") else None
            message = f"[{current_frame.f_code.co_name}]: {message}"
        # 判断是否用例直接调用底层基础方法，则输出info日志
        current_frame1 = sys._getframe(2) if hasattr(sys, "_getframe") else None
        if current_frame1.f_code.co_name.startswith("test_"):
            logging.info(message)
        else:
            logging.debug(message)

    @staticmethod
    def error(message, auteadd=True):
        """error"""
        if len(logging.root.handlers) == 0:
            logger(setting.LOG_LEVEL)
        if auteadd:
            current_frame = sys._getframe(1) if hasattr(sys, "_getframe") else None
            message = f"[{current_frame.f_code.co_name}]: {message}"
        logging.error(message)

    @staticmethod
    def exception(message):
        """exception"""
        if len(logging.root.handlers) == 0:
            logger(setting.LOG_LEVEL)
        logging.exception(message)

    @staticmethod
    def warning(message):
        """warning"""
        if len(logging.root.handlers) == 0:
            logger(setting.LOG_LEVEL)
        logging.warning(message)
