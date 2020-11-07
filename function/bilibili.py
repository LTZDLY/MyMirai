import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict

import requests
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

token = "c6af35ef30f73e1e4ca43e917c5ffd99"
SESSDATA = "ad46c3ff%2C1605266060%2Cd7491*51"
bili_jct = "c6af35ef30f73e1e4ca43e917c5ffd99"
cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + bili_jct


async def sign(app, group):
    url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
    headers = {"cookie": cookie, "room_id": "330091",
               "csrf_token": token, "csrf": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        await app.sendGroupMessage(group, MessageChain.create([Plain("签到成功！本次签到奖励为：" + r.json()["data"]["text"])]))
        await app.sendGroupMessage(group, MessageChain.create([Plain("本月一共签到" + str(r.json()["data"]["hadSignDays"]) + "天")]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))


async def get(app, group):
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "area_v2": "235", "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    addr = r.json()["data"]["rtmp"]["addr"]
    code = r.json()["data"]["rtmp"]["code"]
    if (r.json()["data"]["status"] == "LIVE"):
        await app.sendFriendMessage(349468958, MessageChain.create([Plain(addr)]))
        await app.sendFriendMessage(349468958, MessageChain.create([Plain(code)]))
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间开启成功")]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间开启失败，可能是cookie过期")]))


async def end(app, group):
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    if (r.json()["data"]["status"] == "PREPARING"):
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间关闭成功")]))


async def change(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    title = text[1]
    for i in range(2, len(text)):
        title = title + ' ' + text[i]

    url = "https://api.live.bilibili.com/room/v1/Room/update"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "title": title}
    r = requests.post(url, data, headers=headers)
    if (r.json()["msg"] == "ok"):
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间标题已更改为：\n" + title)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间标题更改失败，可能是cookie过期")]))


async def dayReportCollect(app, group):
    url = "https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report-collect%2Fa"
    cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + \
        bili_jct + '; session-api=3o2l5qds0cepbb2ks73rhn1pks'
    headers = {"cookie": cookie, "csrf_token": token, "csrf": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        s = '公会名称：' + r.json()["data"]["clan_info"]["name"]\
            + '\n当前排名：' + str(r.json()["data"]["clan_info"]["last_ranking"])\
            + '\n当前周目：' + str(r.json()["data"]["boss_info"]["lap_num"])\
            + '\n当前boss：' + r.json()["data"]["boss_info"]["name"]\
            + '\nboss hp：' + str(r.json()["data"]["boss_info"]["current_life"])\
            + ' / ' + str(r.json()["data"]["boss_info"]["total_life"])
        await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))


async def dayReportTotal(app, group, flag=False):
    tt = datetime.now()
    td = timedelta(hours=5)
    t = (tt - td).strftime("%Y-%m-%d")
    url = 'https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report%2Fa&size=30&date=' + t
    cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + \
        bili_jct + '; session-api=3o2l5qds0cepbb2ks73rhn1pks'
    headers = {"cookie": cookie, "csrf_token": token, "csrf": token}
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
        await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))
    pass


async def dayPersonFind(app, group, msg: str, flag=False):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    title = text[1]
    for i in range(2, len(text)):
        title = title + ' ' + text[i]
    tt = datetime.now()
    td = timedelta(hours=5)
    t = (tt - td).strftime("%Y-%m-%d")
    url = 'https://www.bigfun.cn/api/feweb?target=gzlj-clan-day-report%2Fa&size=30&date=' + t
    cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + \
        bili_jct + '; session-api=3o2l5qds0cepbb2ks73rhn1pks'
    headers = {"cookie": cookie, "csrf_token": token, "csrf": token}
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
        await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))
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
        await app.sendGroupMessage(group, MessageChain.create(
            [Plain('error: Invalued input')]))
        return
    page = ran[0] // 25
    ran[0] = ran[0] % 25
    ran[1] = ran[1] % 25
    url = "https://www.bigfun.cn/api/feweb?target=get-gzlj-team-war-work-list%2Fa&type=2&battle_id=4&order=1&page=" + \
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
        await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))
    pass


async def findWorkDetails(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    workid = text[1]
    url = "https://www.bigfun.cn/api/feweb?target=get-gzlj-team-war-work-detail%2Fa&work_id=" + workid
    cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + \
        bili_jct + '; session-api=3o2l5qds0cepbb2ks73rhn1pks'
    headers = {"cookie": cookie, "csrf_token": token, "csrf": token}
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
        await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))
    pass


async def draw(app, group, upflag=False):
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

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
        if upflag == True and i["up"] == 1:
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
        ran = random.uniform(0, 100000)
        if ran > 97500:
            if upflag == True and upstar3 and ran < 98200:
                out.append('【' + random.choice(upstar3) + '】')
                sstr = "おめでとうございます！\n"
            else:
                out.append('【' + random.choice(star3) + '】')
            num3 += 1
        elif ran < 79500:
            out.append(random.choice(star1))
            num1 += 1
        else:
            out.append(random.choice(star2))
            num2 += 1

    ran = random.uniform(0, 100000)
    if ran > 97500:
        if upflag == True and upstar3 and ran < 98200:
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
    if upflag == True and upstar3:
        for i in upstar3:
            sstr += i + ' '
        sstr += 'UP池'
    else:
        sstr += "白金标准池"
    await app.sendGroupMessage(group, MessageChain.create([Plain(sstr)]))
    pass


async def drawauto(app, group, msg: str, upflag=False):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    wanna = text[1]
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    for i in data["data"]:
        if i["name"] == wanna and (i["type"] == 0 or i["up"] == 1):
            break
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain("卡池里没有这个角色哦！")]))
        return
    star3 = []
    star2 = []
    star1 = []
    upstar3 = []
    upstar2 = []
    num3 = 0
    num2 = 0
    num1 = 0

    for i in data["data"]:
        if upflag == True and i["up"] == 1:
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
    while True:
        times += 10
        out = []
        for i in range(0, 9):
            ran = random.uniform(0, 100000)
            if ran > 97500:
                if upflag == True and upstar3 and ran < 98200:
                    out.append(random.choice(upstar3))
                else:
                    out.append(random.choice(star3))
                num3 += 1
            elif ran < 79500:
                out.append(random.choice(star1))
                num1 += 1
            else:
                out.append(random.choice(star2))
                num2 += 1

        ran = random.uniform(0, 100000)
        if ran > 97500:
            if upflag == True and upstar3 and ran < 98200:
                out.append(random.choice(upstar3))
            else:
                out.append(random.choice(star3))
            num3 += 1
        else:
            out.append(random.choice(star2))
            num2 += 1
        if wanna in out:
            break
    stone += 50 * num3 + 10 * num2 + num1
    s = "おめでとうございます！" + \
        "\n消耗石头：" + str(times * 150) + \
        "\n抽卡次数：" + str(times) + \
        "\n获得女神石：" + str(stone) + \
        "\n3星：" + str(num3) + "    2星：" + str(num2) + "    1星：" + str(num1) + \
        "\n当前卡池信息："
    if upflag == True and upstar3:
        for i in upstar3:
            s += i + ' '
        s += 'UP池'
    else:
        s += "白金标准池"
    await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))
    pass


async def setUP(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    wanna = text[1]
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    flag = 0
    for i in data["data"]:
        if i["name"] == wanna:
            i["up"] = 1
            break
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain("卡池里没有这个角色哦！")]))
        return
    await app.sendGroupMessage(group, MessageChain.create([Plain("将" + wanna + "设置为up卡成功！")]))
    with open(Localpath, "w") as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


async def offUP(app, group, msg):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    wanna = text[1]
    Localpath = './data/pcrcharacter.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()
    flag = 0
    for i in data["data"]:
        if i["name"] == wanna:
            i["up"] = 0
            break
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain("卡池里没有这个角色哦！")]))
        return
    await app.sendGroupMessage(group, MessageChain.create([Plain("将" + wanna + "取消up卡成功！")]))
    with open(Localpath, "w") as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()


def id2character(data: Dict, id: str) -> str:
    for i in data["data"]:
        if i["id"] == id:
            return i["name"]
    raise Exception("无效id")


def bilibili(app, group, msg: str):
    if (msg == "bilibili.signup"):
        asyncio.create_task(sign(app, group))
    elif (msg == "bilibili.get"):
        asyncio.create_task(get(app, group))
    elif (msg == "bilibili.end"):
        asyncio.create_task(end(app, group))
    elif (msg.startswith("bilibili.change")):
        asyncio.create_task(change(app, group, msg))


def pcrteam(app, group, msg: str):
    if (msg == "pcrteam.report"):
        asyncio.create_task(dayReportCollect(app, group))
    elif (msg == "pcrteam.daily"):
        asyncio.create_task(dayReportTotal(app, group))
    elif (msg == "pcrteam.daily.details"):
        asyncio.create_task(dayReportTotal(app, group, True))
    elif (msg.startswith("pcrteam.find.details")):
        asyncio.create_task(dayPersonFind(app, group, msg, True))
    elif (msg.startswith("pcrteam.find")):
        asyncio.create_task(dayPersonFind(app, group, msg))
    elif (msg.startswith("pcrteam.work.details")):
        asyncio.create_task(findWorkDetails(app, group, msg))
    elif (msg.startswith("pcrteam.work")):
        asyncio.create_task(findWork(app, group, msg))
    pass


def pcr(app, group, msg: str):
    if (msg.startswith("pcr.draw.setup")):
        asyncio.create_task(setUP(app, group, msg))
    elif (msg.startswith("pcr.draw.offup")):
        asyncio.create_task(offUP(app, group, msg))
    elif (msg.startswith("pcr.draw.up")):
        if msg == "pcr.draw.up":
            asyncio.create_task(draw(app, group, True))
        else:
            asyncio.create_task(drawauto(app, group, msg, True))
    elif (msg.startswith("pcr.draw")):
        if msg == "pcr.draw":
            asyncio.create_task(draw(app, group))
        else:
            asyncio.create_task(drawauto(app, group, msg))


if __name__ == '__main__':
    pass
