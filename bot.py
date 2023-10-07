import datetime
import hashlib
import pkgutil
import time
from threading import Thread

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (HttpClientConfig,
                                             WebsocketClientConfig, config)
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Saya
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

app = Ariadne(
    connection=config(
        1424912867,  # 你的机器人的 qq 号
        "LLSShinoai",  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host="http://localhost:8098"),
        WebsocketClientConfig(host="http://localhost:8098"),
    ),
)

# app = Ariadne(MiraiSession(host="http://localhost:8098",
#                            verify_key="LLSShinoai", account=948153351))

bcc = app.broadcast
inc = InterruptControl(bcc)


saya = create(Saya)

with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        if module_info.name.startswith("_"):
            # 假设模组是以 `_` 开头的，就不去导入
            # 根据 Python 标准，这类模组算是私有函数
            continue
        # print(f"modules.{module_info.name}")
        saya.require(f"modules.{module_info.name}")


def get_md5(file_name) -> str:
    with open(file_name, "rb") as fp:
        data = fp.read()
    return hashlib.md5(data).hexdigest()


def check_change(file_name, mod, typing="change"):
    # print(file_name, mod)
    code = get_md5(file_name)
    while 1:
        time.sleep(1)
        newcode = get_md5(file_name)
        if code == newcode:
            break
        code = newcode
    if typing == "new":
        print(f"对{mod} import")
        saya.require(mod)
        # __import__(mod)
    else:
        print(f"对{mod}热重载")
        # print(mod)
        a = saya.channels.get(mod)
        # print(a)
        saya.reload_channel(a)
        # reload(sys.modules[mod])


class MyHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.t = 0

    def on_modified(self, event):
        # print(event)
        t1 = time.time_ns()
        if self.t == 0:
            self.t = t1
        elif t1 - self.t < 10**9:
            return
        self.t = t1

        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
        if event.src_path[-3:] != ".py":
            print(f"{t}: 文件被修改 {event.src_path}")
            return
        print(f"{t}: 文件被修改 {event.src_path}，执行热重载")
        mod = event.src_path[2:-3].replace("/", ".")
        # time.sleep(1)
        # reload(sys.modules[mod])
        # asyncio.create_task(check_change(event.src_path, mod))
        Thread(target=check_change, args=(event.src_path, mod)).start()

    def on_created(self, event):
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
        if event.src_path[-3:] != ".py":
            print(f"{t}: 文件被创建 {event.src_path}")
            return
        print(f"{t}: 文件被创建 {event.src_path}，执行热重载")
        mod = event.src_path[2:-3].replace("/", ".")
        # time.sleep(1)
        # __import__(pkgname + "." + mod)
        Thread(target=check_change, args=(event.src_path, mod, "new")).start()


def mod_reload():
    # if __name__ == "__main__":
    path = "./modules"
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    pass


Thread(target=mod_reload).start()
app.launch_blocking()
