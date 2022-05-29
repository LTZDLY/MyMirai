import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.data import cookie, token

table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608


def dec(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]]*58**i
    return (r-add) ^ xor


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


async def triple(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    av = 0
    if text[1].startswith("av"):
        av = text[1].replace("av", "")
    elif text[1].startswith("AV"):
        av = text[1].replace("AV", "")
    elif text[1].startswith("BV") or text[1].startswith("bv"):
        av = dec(text[1])

    url = " https://api.bilibili.com/x/web-interface/archive/like/triple"
    headers = {"cookie": cookie}
    data = {"csrf": token, "aid": av}
    r = requests.post(url, data, headers=headers)
    if (r.json()["code"] == 0):
        await app.sendGroupMessage(group, MessageChain.create([Plain("三连成功！")]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain(r.json()["message"])]))


async def bilibili(app, group, msg: str):
    if (msg == "bilibili.signup"):
        await sign(app, group)
    elif (msg == "bilibili.get"):
        await get(app, group)
    elif (msg == "bilibili.end"):
        await end(app, group)
    elif (msg.startswith("bilibili.change")):
        await change(app, group, msg)
    elif (msg.startswith("bilibili.triple")):
        await triple(app, group, msg)
