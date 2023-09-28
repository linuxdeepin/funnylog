# FunnyLog

一个简单易用、功能强大的日志工具。

只需要加一个装饰器，就能自动日志输出类里面所有的方法的功能说明。

---

**Documentation**: <a href="https://linuxdeepin.github.io/funnylog" target="_blank">https://linuxdeepin.github.io/funnylog</a>

**Source Code**: <a href="https://github.com/linuxdeepin/funnylog" target="_blank">https://github.com/linuxdeepin/funnylog</a>

---

## 安装

```console
pip install funnylog
```

## 使用说明

```python
from funnylog import logger
from funnylog import log
from funnylog.conf import setting

setting.CLASS_NAME_ENDSWITH = ("Log",)
logger("DEBUG")


class BaseLog:

    def base_self_method(self):
        """我是 基类 里面的实例方法"""

    @classmethod
    def base_cls_method(self):
        """我是 基类 里面的类方法"""

    @staticmethod
    def base_static_method():
        """我是 基类 里面的静态方法"""

# 注意这里，只需要在这里挂一个装饰器
@log
class TestLog(BaseLog):
    """继承了基类BaseLog"""

    def self_method(self):
        """我是 类 里面的实例方法"""

    @classmethod
    def cls_method(self):
        """我是 类 里面的类方法"""

    @staticmethod
    def static_method():
        """我是 类 里面的静态方法"""


if __name__ == '__main__':
    # @log装饰器自动打印
    TestLog().self_method()
    TestLog().cls_method()
    TestLog().static_method()
    # 直接调用基类里面的方法，也能自动打印
    TestLog().base_self_method()
    TestLog().base_cls_method()
    TestLog().base_static_method()
```

终端输出效果：

<center>    <img style="border-radius: 0.3125em;    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);"     src="./docs/img/log.png">    <br>    <div style="color:orange; border-bottom: 1px solid #d9d9d9;    display: inline-block;    color: #999;    padding: 2px;"></div> </center>