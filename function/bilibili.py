import requests
import json

token = "c6af35ef30f73e1e4ca43e917c5ffd99"
SESSDATA = "ad46c3ff%2C1605266060%2Cd7491*51"
bili_jct = "c6af35ef30f73e1e4ca43e917c5ffd99"
cookie = "SESSDATA=" + SESSDATA + "; bili_jct=" + bili_jct

async def sign(app):
    url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
    headers = {"cookie": cookie, "room_id": "330091",
               "csrf_token": token, "csrf": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        await app.sendFriendMessage("签到成功！本次签到奖励为：" + r.json()["data"]["text"])
        print("本月一共签到" + r.json()["data"]["hadSignDays"] + "天")
    else: 
        print(r.json()["message"])


def get(app):
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "area_v2": "235", "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    addr = r.json()["data"]["rtmp"]["addr"]
    code = r.json()["data"]["rtmp"]["code"]
    if (r.json()["data"]["status"] == "LIVE"):
        print(addr)
        print(code)
        print("直播间开启成功")
    else:
        print("直播间开启失败，可能是cookie过期")


def end(app):
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    if (r.json()["data"]["status"] == "PREPARING"):
        print("直播间关闭成功")


def change(app, msg):
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
        print("直播间标题已更改为：\n" + title)
    else:
        print("直播间标题更改失败，可能是cookie过期")

def bilibili(app, msg: str):
    if (msg == "bilibili.sign"):
        sign(app)
    elif (msg == "bilibili.get"):
        get(app)
    elif (msg == "bilibili.end"):
        end(app)
    elif (msg.startswith("bilibili.change") == 0):
        change(app, msg)
