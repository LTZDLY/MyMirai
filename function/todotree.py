# 两个功能
# 1. 以个人为单位记录要做的事情
# 2. 临时使用，报到证领取队列（超时了，摸了）

import json
import os

help_todo = '''Todo列表：
将你要做的事情记录下来吧！
用法以及参数：
todo.show: 展示你的Todo列表
todo.add [obj]: 将[obj]加入你的Todo列表
todo.rm [inx1] [inx2] ...: 将序号为[inx1]，[inx2]，...的事情从你的Todo列表当中移除
'''


def initTodo():
    Localpath = 'data/todo.json'
    data = {}
    jsObj = json.dumps(data)
    with open(Localpath, "w") as fw:
        fw.write(jsObj)
        fw.close()


def readTodo():
    Localpath = 'data/todo.json'
    if os.path.exists(Localpath) == False:
        initTodo()
    with open(Localpath, 'r', encoding='utf8')as fp:
        data = json.load(fp)
    return data


def getTodo(member, data):
    if not member in data:
        return []
    return data[member]


def setTodo(member, data, thing):
    Localpath = 'data/todo.json'
    if not member in data:
        data[member] = [thing]
    else:
        data[member].append(thing)
    jsObj = json.dumps(data)
    with open(Localpath, "w") as fw:
        fw.write(jsObj)
        fw.close()
    return data[member]


def rmTodo(member, data, num):
    Localpath = 'data/todo.json'
    if not member in data:
        return []
    l = data[member]
    if num > len(l):
        return l
    del (l[num - 1])
    jsObj = json.dumps(data)
    with open(Localpath, "w") as fw:
        fw.write(jsObj)
        fw.close()
    return l


def toMsg(l: list):
    if not l:
        return "没有事情要做了噜~"
    msg = "要做的事情："
    for i in range(0, len(l)):
        msg += f"\n{i + 1}. {l[i]}"
    return msg


def funTodo(msg, member):
    member = str(member)
    text = msg.split(' ', 1)
    data = readTodo()
    if msg == 'todo.show':
        l = getTodo(member, data)
        return toMsg(l)
    if text[0] == 'todo.add':
        if len(text) < 2:
            return
        l = setTodo(member, data, text[1])
        return toMsg(l)
    if text[0] == 'todo.rm':
        lit = text[1].split(' ')
        num = []
        for i in lit:
            try:
                num.append(int(i))
            except:
                pass
        num.sort(reverse=True)
        for i in num:
            l = rmTodo(member, data, i)
        return toMsg(l)
    pass


if __name__ == "__main__":
    while (1):
        msg = input()
        funTodo(msg, 123)
    pass
