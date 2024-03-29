# 两个功能
# 1. 以个人为单位记录要做的事情
# 2. 临时使用，报到证领取队列（超时了，摸了）

import json
import os

help_todo = """Todo列表：
将你要做的事情记录下来吧！
用法以及参数：
todo(.tablename).show (tablename): 展示你的Todo列表(中名为tablename的表)
todo(.tablename).add [obj]: 将[obj]加入你的Todo列表(中名为tablename的表)
todo(.tablename).rm [inx1] [inx2] ...: 将序号为[inx1]，[inx2]，...的事情从你的Todo列表(中名为tablename的表)当中移除
"""


def initTodo():
    Localpath = "data/todo.json"
    data = {}
    jsObj = json.dumps(data)
    with open(Localpath, "w", encoding="utf8") as fw:
        fw.write(jsObj)
        fw.close()


def readTodo():
    Localpath = "data/todo.json"
    if os.path.exists(Localpath) == False:
        initTodo()
    with open(Localpath, "r", encoding="utf8") as fp:
        data = json.load(fp)
    return data


def getTodo(member, data, form_name):
    # 没有该成员的数据或该成员的数据为空
    if not member in data or not data[member]:
        return "完全没有事情要做了噜~"
    # 本表的数据不为空
    if form_name in data[member]:
        return toMsg(data[member][form_name], form_name)
    # 本表的数据为空
    s = f"{form_name}表中没有事情要做了噜~"
    if data[member]:
        l = 0
        for i in data[member]:
            l += len(data[member][i])
        s += "\n但是，" 
        s += "，".join((str(i) + "表") for i in data[member])
        s += f"中还有{l}件事情需要处理，现在还不能休息哦。"
    return s


def setTodo(member, data, thing, form_name):
    Localpath = "data/todo.json"
    if not form_name:
        form_name = "defalt"
    if not member in data:
        data[member] = {form_name: [thing]}
    else:
        if not form_name in data[member]:
            data[member][form_name] = [thing]
        else:
            data[member][form_name].append(thing)
    jsObj = json.dumps(data)
    with open(Localpath, "w", encoding="utf8") as fw:
        fw.write(jsObj)
        fw.close()
    return data[member][form_name]


def rmTodo(member, data, num, form_name):
    Localpath = "data/todo.json"
    if not member in data:
        return []
    if not form_name:
        form_name = "defalt"
    if not form_name in data[member]:
        return []
    l = data[member][form_name]
    if num > len(l):
        return l
    del l[num - 1]
    if not data[member][form_name]:
        del data[member][form_name]
    jsObj = json.dumps(data)
    with open(Localpath, "w", encoding="utf8") as fw:
        fw.write(jsObj)
        fw.close()
    return l


def showtoMsg(l: list):
    if not l:
        return "没有事情要做了噜~"
    msg = "要做的事情："
    for i in range(0, len(l)):
        msg += f"\n{i + 1}. {l[i]}"
    return msg


def toMsg(l: list, form_name: str):
    if not l:
        return f"{form_name}表中没有事情要做了噜~"
    msg = f"{form_name}表中要做的事情："
    for i in range(0, len(l)):
        msg += f"\n{i + 1}. {l[i]}"
    return msg


def funTodo(msg, member):
    member = str(member)
    text = msg.split(" ", 1)
    txt = text[0].split(".")
    if len(txt) == 3:
        form_name = txt[1]
        command = txt[2]
    elif len(txt) == 2:
        form_name = ""
        command = txt[1]
    data = readTodo()
    if command == "show":
        if not form_name and len(text) > 1:
            form_name = text[1]
        elif not form_name:
            form_name = "默认"
        return getTodo(member, data, form_name)
    if command == "add":
        if not form_name:
            form_name = "默认"
        if len(text) < 2:
            return
        l = setTodo(member, data, text[1], form_name)
        return toMsg(l, form_name)
    if command == "rm":
        if not form_name:
            form_name = "默认"
        lit = text[1].split(" ")
        num = []
        for i in lit:
            try:
                num.append(int(i))
            except:
                pass
        num.sort(reverse=True)
        for i in num:
            l = rmTodo(member, data, i, form_name)
        return getTodo(member, data, form_name)
    pass


if __name__ == "__main__":
    while 1:
        msg = input()
        print(funTodo(msg, 123))
    pass

# todo.表名.show
# todo.表名.add
# todo.表名.rm
