# FunnyLog

一个简单易用、功能强大的日志工具。

---

**Documentation**: <a href="https://funny-test.github.io/funnylog" target="_blank">https://funny-test.github.io/funnylog</a>

**Source Code**: <a href="https://github.com/funny-test/funnylog" target="_blank">https://github.com/funny-test/funnylog</a>



## 安装

```console
pip install funnylog
```

## 使用方法

### 1、自动输出日志

```python
{!../example/log.py!}
```

终端输出：

![](./img/log.png)

### 2、方法中输出其他的日志

```python
{!../example/inside.py!}
```

终端输出：

![](./img/inside.png)

### 3、在外层其他直接使用

```python
{!../example/outside.py!}
```

终端输出：

![](./img/outside.png)



## 必要配置项

- `LOG_FILE_PATH` 日志文件的生成路径；

  默认是在：`/tmp/_logs`，你可以配置为其他位置；

  ```python
  from funnylog.conf import setting
  
  setting.LOG_FILE_PATH = "/home/user/xxx"
  ```

- `LOG_LEVEL`日志级别；

  默认日志输出级别为 `DEBUG` 级别，同样可以进行配置修改；

  ```python
  from funnylog.conf import setting
  
  setting.LOG_LEVEL = "INFO"
  ```

- 自动输出日志的类名称；（tuple）

  - `CLASS_NAME_STARTSWITH` 类名以什么开头；

    ```python
    from funnylog.conf import setting
    
    setting.CLASS_NAME_STARTSWITH = ("Test",) 
    # 注意给元组类型
    ```

  - `CLASS_NAME_ENDSWITH` 类名以什么结尾；

  - `CLASS_NAME_CONTAIN` 类名包含什么字符；