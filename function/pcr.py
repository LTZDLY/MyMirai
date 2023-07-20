import json
import random
import time
import datetime
from typing import Dict

import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.data import pcr_cookie as cookie, pcr_token as token

uprear = 7000
srear = 25000
rear = 180000
sum = 1000000
normal = sum - rear - srear


def short2name(data: Dict, short: str) -> str:
    for i in data["data"]:
        if short in i["short"]:
            return i["name"]
    return short


async def dayReportCollect(app, group):
    url = "https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report-collect%2Fa"
    headers = {"cookie": cookie, "x_csrf_token": token}
    r = requests.get(url, headers=headers)
    life = {6000000: '1', 8000000: '2',
            10000000: '3', 12000000: '4',
            20000000: '5', 15000000: '5'}
    if (r.json()["code"] == 0):
        s = '公会名称：' + r.json()["data"]["clan_info"]["name"]\
            + '\n当前排名：' + str(r.json()["data"]["clan_info"]["last_ranking"])\
            + '\n当前周目：' + str(r.json()["data"]["boss_info"]["lap_num"])\
            + '\n当前boss：' + r.json()["data"]["boss_info"]["name"] + '（' + life[r.json()["data"]["boss_info"]["total_life"]] + '王）'\
            + '\nboss hp：' + str(r.json()["data"]["boss_info"]["current_life"])\
            + ' / ' + str(r.json()["data"]["boss_info"]["total_life"])
        await app.send_group_message(group, MessageChain([Plain(s)]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))


async def dayReportTotal(app, group, flag=False):
    tt = datetime.datetime.now()
    td = datetime.timedelta(hours=5)
    t = (tt - td).strftime("%Y-%m-%d")
    url = 'https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report%2Fa&size=30&date=' + t
    headers = {"cookie": cookie, "x_csrf_token": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        num = 0
        membernum = 0
        s = '今日未出满3刀的人有：'
        for i in r.json()["data"]:
            num += i["number"]
            if i["number"] != 3:
                membernum += 1
                s += '\n' + i["name"]
        if num == 90:
            s = '今天的刀全部出完辣！'
        else:
            if flag == True:
                s = '今日未出满3刀人数：' + str(membernum) + ' / ' + str(len(r.json()["data"]))\
                    + '\n今日出刀总数：' + str(num) + ' / ' + str(3 * len(r.json()["data"]))\
                    + '\n' + s
            else:
                s = '今日未出满3刀人数：' + str(membernum) + ' / ' + str(len(r.json()["data"]))\
                    + '\n今日出刀总数：' + str(num) + ' / ' + \
                    str(3 * len(r.json()["data"]))
        await app.send_group_message(group, MessageChain([Plain(s)]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))
    pass


async def dayPersonFind(app, group, msg: str, flag=False):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    title = text[1]
    for i in range(2, len(text)):
        title = title + ' ' + text[i]
    tt = datetime.datetime.now()
    td = datetime.timedelta(hours=5)
    t = (tt - td).strftime("%Y-%m-%d")
    url = 'https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report%2Fa&size=30&date=' + t
    headers = {"cookie": cookie, "x_csrf_token": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        s = ''
        for i in r.json()["data"]:
            if(i["name"].find(title) == -1):
                continue
            s = i["name"] + '\n今日出刀数：' + str(i["number"]) +\
                '\n造成伤害：' + str(i["damage"]) +\
                '\n得分：' + str(i["score"])
            if(flag == False):
                break
            ss = ''
            num = 1
            for j in i["damage_list"]:
                ss += '\n第' + str(num).rstrip('.0') + '刀：' +\
                    '\n时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(j["datetime"])) +\
                    '\nboss：' + j["boss_name"] +\
                    '\n伤害：' + str(j["damage"])
                if j["kill"] != 0:
                    ss += '，尾刀'
                    num += 0.5
                elif j["reimburse"] != 0:
                    ss += '，补偿刀'
                    num += 0.5
                else:
                    ss += ''
                    num += 1
            s += ss
            break
        if s == '':
            s = '查无此人，请确认id输入正确'
        await app.send_group_message(group, MessageChain([Plain(s)]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))
    pass


async def findWork(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    title = text[1]
    if(len(text) == 3):
        ran = list(map(int, text[2].split('-')))
        if ran[0] != 0:
            ran[0] -= 1
        ran[1] -= 1
    else:
        ran = [0, 5]
    if ((ran[0] // 25) != (ran[1] // 25)):
        await app.send_group_message(group, MessageChain(
            [Plain('error: Invalued input')]))
        return
    page = ran[0] // 25
    ran[0] = ran[0] % 25
    ran[1] = ran[1] % 25
    url = "https://www.bigfun.cn/api/feweb?target=get-gzlj-team-war-work-list%2Fa&type=2&battle_id=8&order=1&page=" + \
        str(page) + "&boss_position=" + title
    r = requests.get(url)

    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    if (r.json()["code"] == 0):
        s = title + '王，共' + str(r.json()['pagination']['total_count']) + \
            '个结果，当前显示第' + str(ran[0] + 1) + '-' + str(ran[1]) + '个结果'
        for j in r.json()["data"][ran[0]:ran[1]]:
            s += '\nid：' + str(j["id"]) + \
                '\n标题：' + j["title"] + \
                '\n周目：' + str(j["boss_cycle"]) + \
                '\n期望伤害：' + str(j["expect_injury"]) + \
                '\n角色：'
            for i in j["role_list"]:
                s += id2character(data, i["id"]) + ' '
            pass
        await app.send_group_message(group, MessageChain([Plain(s)]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))
    pass


async def findWorkDetails(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    workid = text[1]
    url = "https://www.bigfun.cn/api/feweb?target=get-gzlj-team-war-work-detail%2Fa&work_id=" + workid
    headers = {"cookie": cookie, "x_csrf_token": token}
    r = requests.get(url, headers=headers)

    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    if (r.json()["code"] == 0):
        s = 'id：' + workid + \
            '\n公会战：' + r.json()["data"]["battle_info"]["name"] + \
            '\n标题：' + r.json()["data"]["title"] + \
            '\nboss：' + r.json()["data"]["boss"]["name"] + \
            '\n周目：' + str(r.json()["data"]["boss_cycle"]) + \
            '\n期望伤害：' + str(r.json()["data"]["expect_injury"]) + \
            '\n角色：'
        role = json.loads(r.json()["data"]["role_list"])
        for i in role:
            s += id2character(data, i["id"]) + str(i["stars"]) + '星'
            if i["weapons"] == 1:
                s += '专武 '
            else:
                s += ' '
        s += '\n作业轴：\n' + r.json()["data"]["work"]
        if(r.json()["data"]["remark"] != ''):
            s += '\n备注：' + r.json()["data"]["remark"]
        await app.send_group_message(group, MessageChain([Plain(s)]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))
    pass


async def expand(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    wanna = short2name(data, text[1])
    if wanna != text[1]:
        await app.send_group_message(group, MessageChain([Plain(text[1] + " 可能是 " + wanna + " 的缩写")]))
    else:
        await app.send_group_message(group, MessageChain([Plain("并未查到是什么的缩写，是本名也说不定哦！")]))


async def draw(app, group, upflag=False):
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    if upflag and data["double"]:
        global srear
        srear = 25000 * 2
    else:
        srear = 25000
    star3 = []
    star2 = []
    star1 = []
    upstar3 = []
    upstar2 = []
    out = []
    num3 = 0
    num2 = 0
    num1 = 0
    sstr = ""

    for i in data["data"]:
        if upflag and i["up"] == 1:
            if i["star"] == 3:
                upstar3.append(i["name"])
            elif i["star"] == 2:
                upstar2.append(i["name"])
        else:
            if i["type"] != 0:
                continue
            if i["star"] == 3:
                star3.append(i["name"])
            elif i["star"] == 2:
                star2.append(i["name"])
            elif i["star"] == 1:
                star1.append(i["name"])

    for i in range(0, 9):
        ran = random.uniform(0, sum)
        if ran > sum - srear:
            if upflag == True and upstar3 and ran < sum - srear + uprear:
                out.append('【' + random.choice(upstar3) + '】')
                sstr = "おめでとうございます！\n"
            else:
                out.append('【' + random.choice(star3) + '】')
            num3 += 1
        elif ran < normal:
            out.append(random.choice(star1))
            num1 += 1
        else:
            out.append(random.choice(star2))
            num2 += 1

    ran = random.uniform(0, sum)
    if ran > sum - srear:
        if upflag == True and upstar3 and ran < sum - srear + uprear:
            out.append(random.choice(upstar3))
            sstr = "おめでとうございます！\n"
        else:
            out.append('【' + random.choice(star3) + '】')
        num3 += 1
    else:
        out.append(random.choice(star2))
        num2 += 1
    if sstr == "":
        sstr = "素敵な仲間が増えますよ！\n"
    for i in range(0, 5):
        sstr += out[i] + ' '
    sstr += '\n'
    for i in range(5, 10):
        sstr += out[i] + ' '
    sstr += "\n3星：" + str(num3) + "    2星：" + str(num2) + "    1星：" + str(num1) + \
        "\n女神石：" + str(50 * num3 + 10 * num2 + num1) + '\n当前卡池信息：'
    if upflag and data['double']:
        sstr += '三星概率双倍 '
    if upflag == True and upstar3:
        for i in upstar3:
            sstr += i + ' '
        sstr += 'UP池'
    else:
        sstr += "白金标准池"
    await app.send_group_message(group, MessageChain([Plain(sstr)]))
    pass


async def drawauto(app, group, msg: str, upflag=False):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    if upflag and data["double"]:
        global srear
        srear = 25000 * 2
    else:
        srear = 25000
    wanna = short2name(data, text[1])
    for i in data["data"]:
        if i["name"] == wanna and (i["type"] == 0 or (upflag and i["up"] == 1)):
            break
    else:
        await app.send_group_message(group, MessageChain([Plain("卡池里没有这个角色哦！")]))
        return
    star3 = []
    star2 = []
    star1 = []
    upstar3 = []
    upstar2 = []
    num3 = 0
    num2 = 0
    num1 = 0
    star3get = {}
    for i in data["data"]:
        if upflag and i["up"] == 1:
            if i["star"] == 3:
                upstar3.append(i["name"])
            elif i["star"] == 2:
                upstar2.append(i["name"])
        else:
            if i["type"] != 0:
                continue
            if i["star"] == 3:
                star3.append(i["name"])
            elif i["star"] == 2:
                star2.append(i["name"])
            elif i["star"] == 1:
                star1.append(i["name"])
    stone = 0
    times = 0
    crt = ""
    while True:
        times += 10
        out = []
        for i in range(0, 9):
            ran = random.uniform(0, sum)
            if ran > sum - srear:
                if upflag == True and upstar3 and ran < sum - srear + uprear:
                    crt = random.choice(upstar3)
                    out.append(crt)
                else:
                    crt = random.choice(star3)
                    out.append(crt)
                num3 += 1
                if not crt in star3get:
                    star3get[crt] = 1
                else:
                    star3get[crt] += 1
            elif ran < normal:
                out.append(random.choice(star1))
                num1 += 1
            else:
                out.append(random.choice(star2))
                num2 += 1

        ran = random.uniform(0, sum)
        if ran > sum - srear:
            if upflag == True and upstar3 and ran < sum - srear + uprear:
                crt = random.choice(upstar3)
                out.append(crt)
            else:
                crt = random.choice(star3)
                out.append(crt)
            num3 += 1
            if not crt in star3get:
                star3get[crt] = 1
            else:
                star3get[crt] += 1
        else:
            out.append(random.choice(star2))
            num2 += 1
        if wanna in out:
            break
    stone += 50 * num3 + 10 * num2 + num1
    s = "おめでとうございます！" + \
        "\n" + wanna + " 抽出来啦！" + \
        "\n消耗石头：" + str(times * 150) + \
        "\n抽卡次数：" + str(times) + \
        "\n获得女神石：" + str(stone) + \
        "\n3星：" + str(num3) + "    2星：" + str(num2) + "    1星：" + str(num1) + \
        "\n当前卡池信息："
    if upflag and data['double']:
        s += '三星概率双倍 '
    if upflag == True and upstar3:
        for i in upstar3:
            s += i + ' '
        s += 'UP池'
    else:
        s += "白金标准池"
    s += "\n三星出货信息："
    if num3 == 0:
        s += "\n无"
    else:
        for c in star3get:
            s += "\n" + c + "：" + str(star3get[c])
    await app.send_group_message(group, MessageChain([Plain(s)]))
    pass


async def setUP(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    wanna = short2name(data, text[1])
    for i in data["data"]:
        if wanna == i["name"]:
            i["up"] = 1
            break
    else:
        await app.send_group_message(group, MessageChain([Plain("卡池里没有这个角色哦！")]))
        return
    await app.send_group_message(group, MessageChain([Plain("将" + wanna + "设置为up卡成功！")]))
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def offUP(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    wanna = short2name(data, text[1])
    for i in data["data"]:
        if wanna == i["name"]:
            i["up"] = 0
            break
    else:
        await app.send_group_message(group, MessageChain([Plain("卡池里没有这个角色哦！")]))
        return
    await app.send_group_message(group, MessageChain([Plain("将" + wanna + "取消up卡成功！")]))
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def setD(app, group):
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    data["double"] = True
    await app.send_group_message(group, MessageChain([Plain("将卡池设为双倍三星概率成功！")]))
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def offD(app, group):
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    data["double"] = False
    await app.send_group_message(group, MessageChain([Plain("将卡池取消双倍三星概率成功！")]))
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def setDefine(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 3):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    wanna = short2name(data, text[1])
    for i in data["data"]:
        if wanna == i["name"]:
            if not text[2] in i["short"]:
                i["short"].append(text[2])
                await app.send_group_message(group, MessageChain([Plain("添加缩写：" + wanna + " 缩写为 " + text[2])]))
            break
    else:
        await app.send_group_message(group, MessageChain([Plain("卡池里没有这个角色哦！")]))
        return
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def offDefine(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 3):
        return
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    wanna = short2name(data, text[1])
    for i in data["data"]:
        if wanna == i["name"]:
            if text[2] in i["short"]:
                i["short"].remove(text[2])
                await app.send_group_message(group, MessageChain([Plain("删除缩写：" + wanna + " 缩写为 " + text[2])]))
            else:
                await app.send_group_message(group, MessageChain([Plain(wanna + "没有这个缩写哦！")]))
            break
    else:
        await app.send_group_message(group, MessageChain([Plain("卡池里没有这个角色哦！")]))
        return
    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


def id2character(data: Dict, id: str) -> str:
    for i in data["data"]:
        if i["id"] == id:
            return i["name"]
    raise Exception("无效id")


async def pcrteam(app, group, msg: str):
    if (msg == "pcrteam.report"):
        await dayReportCollect(app, group)
    elif (msg == "pcrteam.daily"):
        await dayReportTotal(app, group)
    elif (msg == "pcrteam.daily.details"):
        await dayReportTotal(app, group, True)
    elif (msg.startswith("pcrteam.find.details")):
        await dayPersonFind(app, group, msg, True)
    elif (msg.startswith("pcrteam.find")):
        await dayPersonFind(app, group, msg)
    elif (msg.startswith("pcrteam.work.details")):
        await findWorkDetails(app, group, msg)
    elif (msg.startswith("pcrteam.work")):
        await findWork(app, group, msg)
    pass


async def pcr(app, group, msg: str):
    if (msg.startswith("pcr.expand")):
        await expand(app, group, msg)
    if (msg.startswith("pcr.define")):
        await setDefine(app, group, msg)
    elif (msg.startswith("pcr.offdefine")):
        await offDefine(app, group, msg)
    elif (msg.startswith("pcr.draw.setup")):
        await setUP(app, group, msg)
    elif (msg.startswith("pcr.draw.offup")):
        await offUP(app, group, msg)
    elif (msg.startswith("pcr.draw.setd")):
        await setD(app, group)
    elif (msg.startswith("pcr.draw.offd")):
        await offD(app, group)
    elif (msg.startswith("pcr.draw.up")):
        if msg == "pcr.draw.up":
            await draw(app, group, True)
        else:
            await drawauto(app, group, msg, True)
    elif (msg.startswith("pcr.draw")):
        if msg == "pcr.draw":
            await draw(app, group)
        else:
            await drawauto(app, group, msg)


if __name__ == '__main__':
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    for i in data["data"]:
        print(i["name"])
        aa = []
        temp = ''
        while True:
            temp = input()
            if temp == '-1':
                break
            aa.append(temp)
            pass
        i["short"] = aa
        pass

    with open(Localpath, "w", encoding='utf8') as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()
    pass
