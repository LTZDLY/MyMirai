
import datetime
import json
import os
import random

from graia.ariadne.entry import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.ini import read_from_ini, write_in_ini


def signup(id: int) -> str:
    date = (read_from_ini('data\\签到.ini', str(id), 'date', '1970-01-01'))
    date = datetime.datetime.fromisoformat(date)
    now = datetime.datetime.today()
    add = datetime.timedelta(hours=7)

    now -= add
    delta = now - date
    if(delta.days == 1):
        num = 1 + int(read_from_ini('data\\签到.ini', str(id), 'num', '0'))
    elif(delta.days == 0):
        sstr = "您今天已经签到过了！"
        return sstr
    else:
        num = 1
    write_in_ini('data\\签到.ini', str(id), 'num', str(num))
    write_in_ini('data\\签到.ini', str(id), 'date', str(now.date()))
    sstr = "签到成功！当前连续签到"+str(num)+"天"
    return sstr


def atme(msg: str) -> bool:
    Localpath = './data/data.json'
    data = {}
    if os.path.exists(Localpath) == False:
        return False
    else:
        fr = open(Localpath, encoding='utf-8')
        data = json.load(fr)
        fr.close()
        if not('Monitor' in data):
            return False
    for i in data['Monitor']:
        if(msg.find(i) != -1):
            return True
    return False


def choice(msg: str) -> str:
    if (msg.find('mirai:image') != -1):
        return '选项暂不支持图像哦'
    if (msg == ''):
        return '你选项呢（恼'
    text = msg.split(' ')
    for i in text:
        if i == '':
            text.remove(i)
    if (len(text) == 1):
        return '只有一项就不用选了吧'
    if (len(text) > 50):
        return '选项太多选不过来了呜呜呜'
    r = -1
    while r == -1 or r == len(text):
        r = random.randint(-1, len(text))
    return text[r]


def loadDefine():
    Localpath = './data/data.json'
    data = {}
    if os.path.exists(Localpath) == False:
        return {}
    else:
        fr = open(Localpath, encoding='utf-8')
        data = json.load(fr)
        fr.close()
        if not('Define' in data):
            return {}
    return data['Define']


def define(msg: str):
    msg = msg.replace('define ', '', 1)
    if(msg.find('->') == -1):
        return
    msg.replace('define ', '', 1)
    text = msg.split('->')
    data = loadDefine()
    Localpath = './data/data.json'
    data[text[0]] = text[1]
    if os.path.exists(Localpath) == False:
        jsObj = {'Define': data}
        jsObj = json.dumps(jsObj, ensure_ascii=False)
        with open(Localpath, "w") as fw:
            fw.write(jsObj)
            fw.close()
    else:
        fr = open(Localpath, encoding='utf-8')
        jsObj = json.load(fr)
        fr.close()
        data_new = {"Define": data}
        for i in data_new:
            jsObj[i] = data_new[i]
        with open(Localpath, "w") as fw:
            jsObj = json.dumps(jsObj)
            fw.write(jsObj)
            fw.close()

    pass


async def paraphrase(app, group: Group, msg: str, feedback=False) -> str:
    data = loadDefine()
    for i in data:
        if msg.find(data[i] == -1):
            continue
        if feedback == True:
            await app.send_group_message(group, MessageChain(__root__=[Plain('发生转义：\n' + i + '->' + data[i])]))
        msg = msg.replace(i, data[i])
    return msg
