# 此为使用另一库实现的弹幕姬源码，可以直接运行使用。
# 因原库在服务器上运行时会有不明原因导致失败，故寻找另一库重新实现该功能，效果良好
# 参考：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/message_stream.md

import asyncio
import datetime
import json
import zlib

import brotli
import requests

# import speech
from aiowebsocket.converses import AioWebSocket

remote = "wss://tx-gz-live-comet-01.chat.bilibili.com/sub"

hb = "00000010001000010000000200000001"


def get_data(room_id):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "cookie": data["shinoai"]["cookie"],
    }
    s = requests.session()
    url = "https://data.bilibili.com/v/"
    r = s.get(url, headers=headers)
    if r.status_code == 200:
        # print(r.cookies)
        buvid = r.cookies["buvid3"]

    """生成握手包数据"""
    # 获取token
    url = (
        "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id=%s&type=0"
        % room_id
    )
    r = s.get(url, headers=headers)
    print(r.json())
    if r.json()["code"] == 0:
        key = r.json()["data"]["token"]
        global remote
        remote = f"wss://{r.json()['data']['host_list'][0]['host']}/sub"

    # 握手包数据内容
    data_json = {
        "uid": 8012418,
        "roomid": int(room_id),
        "protover": 3,
        "platform": "web",
        #  'clientver': '2.6.41',
        "type": 2,
        "key": key,
        "buvid": buvid,
    }
    text = json.dumps(data_json)

    # 握手包数据头
    # 数据头长度为16，[1:4]为数据包长度，[5:6]为数据包头部长度，固定为16，[7:8]为协议版本，目前为1，
    # [9:12]为操作码，握手包为7代表认证并加入房间，[13:16]为sequence，可以取常数1

    # 对应为 长度[\x00\x00\x01\x02] 头部长度[\x00\x10] 协议版本[\x00\x01] 操作码[\x00\x00\x00\x07] sequence[\x00\x00\x00\x01]
    size = len(text) + 16  # 十进制下的数据包总长度
    bytesize = hex(size)[2:]  # 十六进制下的数据包总长度
    data_head = (
        "0" * (8 - len(bytesize)) + bytesize + "001000010000000700000001"
    )  # 对长度补0并且将除了长度之后的内容进行拼接

    data_text = text.encode("ascii")  # 将数据包内容转为bytes型
    data = data_head + data_text.hex()  # 将数据包头和数据包内容进行拼接之后返回
    return bytes.fromhex(data)


async def startup(room_id: str):
    d = get_data(room_id)
    async with AioWebSocket(remote) as aws:
        converse = aws.manipulator
        await converse.send(d)
        tasks = asyncio.create_task(sendHeartBeat(converse, room_id))
        while True:
            recv_text = await converse.receive()
            # print(recv_text)
            printDM(recv_text)


async def sendHeartBeat(websocket, room_id):
    """每30秒发送心跳包"""
    while True:
        await asyncio.sleep(30)
        await websocket.send(bytes.fromhex(hb))
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
        print(f"{t}[NOTICE]: {room_id}: Sent HeartBeat.")


# async def receDM(websocket):
#     while True:
#         recv_text = await websocket.receive()
#         printDM(recv_text)

# 将数据包传入：


def printDM(data):
    # 如果传入的data为null则直接返回
    if not data:
        return

    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
    if len(data) > packetLen:
        printDM(data[packetLen:])
        data = data[:packetLen]

    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    if ver == 1:
        if op == 3:
            t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
            print(f"{t}[RENQI] {int(data[16:].hex(), 16)}")
            pass

    # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
    elif ver == 2:
        data = zlib.decompress(data[16:])
        printDM(data)
        return

    elif ver == 3:
        data = brotli.decompress(data[16:])
        printDM(data)
        return

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    elif ver == 0:
        # print(data)
        if op == 5:
            jd = json.loads(data[16:].decode("utf-8", errors="ignore"))
            # print(jd)
            t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
            sstr = t
            if jd["cmd"] == "DANMU_MSG":
                sstr += f"[DANMU] {jd['info'][2][1]}: {jd['info'][1]}"
                # speech.say(f"{jd['info'][2][1]}说，{jd['info'][1]}")
            elif jd["cmd"] == "LIVE":
                sstr += "[Notice] LIVE Start!"
                # speech.say("直播已开始")
            elif jd["cmd"] == "PREPARING":
                sstr += "[Notice] LIVE Ended!"
                # speech.say("直播已结束")
            elif jd["cmd"] == "SEND_GIFT":
                sstr += (
                    "[GIFT]"
                    + jd["data"]["uname"]
                    + " "
                    + jd["data"]["action"]
                    + " "
                    + str(jd["data"]["num"])
                    + "x"
                    + jd["data"]["giftName"]
                )
                # speech.say(f"感谢{jd['data']['uname']}赠送的{jd['data']['num']}个{jd['data']['giftName']}")
            elif jd["cmd"] == "INTERACT_WORD":
                if jd["data"]["msg_type"] == 1:
                    # print(jd['data'])
                    sstr += f"[ENTRY] {jd['data']['uname']}({jd['data']['uid']}) 进入直播间"
                    # speech.say(f"欢迎{jd['data']['uname']}进入直播间")
                elif jd["data"]["msg_type"] == 2:
                    sstr += "[FOLLOW] " + jd["data"]["uname"] + " 关注了直播间"
            elif jd["cmd"] == "未知":
                print(jd)
                sstr += "[SHARE] " + jd["data"]["uname"] + " 分享了直播间"
            else:
                sstr += "[OTHER] " + jd["cmd"]
                pass

            if sstr != "":
                print(sstr)

    else:
        print(data)


if __name__ == "__main__":
    roomid = int(input("请输入房间号"))
    asyncio.get_event_loop().run_until_complete(startup(roomid))
