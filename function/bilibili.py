import requests
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

token = "af0d842e99dcfd96ddc481593c1fd172"
SESSDATA = "0657b11a%2C1626102289%2Ce4a13*11"
bili_jct = "af0d842e99dcfd96ddc481593c1fd172"
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

async def bilibili(app, group, msg: str):
    if (msg == "bilibili.signup"):
        await sign(app, group)
    elif (msg == "bilibili.get"):
        await get(app, group)
    elif (msg == "bilibili.end"):
        await end(app, group)
    elif (msg.startswith("bilibili.change")):
        await change(app, group, msg)
        