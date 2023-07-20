import datetime
import hashlib
import os
import pkgutil
import sys
import time
from importlib import reload
from threading import Thread

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

pkgpath = os.path.dirname(__file__)
pkgname = os.path.basename(pkgpath)


for _, file, _ in pkgutil.iter_modules([pkgpath]):
    # print(pkgname + "." + file)
    __import__(pkgname + "." + file)


# import function.arknights
# import function.bilibili
# # import function.canvas
# import function.cherugo
# import function.danmaku
# import function.excel
# import function.image
# import function.ini
# import function.latex
# import function.leetcode
# import function.mute
# import function.ouen
# import function.pcr
# import function.permission
# import function.portune
# import function.private
# import function.repeat
# import function.signup
# import function.switch
# import function.todotree
# import function.weather


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
        __import__(mod)
    else:
        print(f"对{mod}热重载")
        reload(sys.modules[mod])


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


# if __name__ == "__main__":
path = f"./{pkgname}"
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

# try:
#     while True:
#         time.sleep(1)

# except KeyboardInterrupt:
#     observer.stop()
