# 此为使用另一库实现的直播监听功能代码。
# 因原库在服务器上运行时会有不明原因导致失败，故寻找另一库重新实现该功能，效果良好


import asyncio
import datetime
import json
import zlib

import brotli
import requests
from aiowebsocket.converses import AioWebSocket
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain

from function.logger import logger

remote = "wss://broadcastlv.chat.bilibili.com:2245/sub"

# 心跳包为不携带数据的数据包，仅包含数据包头部信息，具体代表如后文所示。其中，心跳包的操作码为2
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
    if r.json()["code"] == 0:
        key = r.json()["data"]["token"]
        global remote
        remote = f"wss://{r.json()['data']['host_list'][0]['host']}/sub"

    # 握手包数据内容
    data_json = {
        "uid": data["shinoai"]["uid"],
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


async def entrence(app, room_id):
    """弹幕服务器接入口"""
    await startup(app, room_id)
    num = 0
    while True:
        num += 1
        logger.info(f"[ERROR]: {room_id}: 连接断开，正在尝试第{num}次重连.")
        await startup(app, room_id)


async def startup(app, room_id: str):
    """创建ws连接b站弹幕服务器"""
    d = get_data(room_id)
    async with AioWebSocket(remote) as aws:
        converse = aws.manipulator
        await converse.send(d)
        tasks = asyncio.create_task(sendHeartBeat(converse, room_id))
        logger.info(f"[NOTICE]: 开启对房间号{room_id}的视奸")
        try:
            while True:
                recv_text = await converse.receive()
                await printDM(app, recv_text, room_id)
        except Exception as e:
            tasks.cancel()
            if str(e) == "断开连接":
                await asyncio.sleep(300)
            await asyncio.sleep(30)


async def sendHeartBeat(websocket, room_id):
    """每30秒发送心跳包"""
    while True:
        await asyncio.sleep(30)
        await websocket.send(bytes.fromhex(hb))
        # logger.info(f"[NOTICE]: {room_id}: Sent HeartBeat.")


# 将数据包传入：


async def printDM(app, data, room_id):
    """解析并输出数据包的数据"""
    # 如果传入的data为null则直接返回
    if not data:
        return

    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
    if len(data) > packetLen:
        await printDM(app, data[packetLen:], room_id)
        data = data[:packetLen]

    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    # if ver == 1:
    #     if op == 3:
    #         t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
    #         t = t[: len(t) - 3] + "]"
    #         print("%s[POPULARITY]: %s: %d" % (t, room_id, int(data[16:].hex(), 16)))
    #     return

    # ver 为2的时候代表接收到的是 zlib 压缩的数据包，这个时候要去解压。
    if ver == 2:
        data = zlib.decompress(data[16:])
        await printDM(app, data, room_id)
        return

    # ver 为3的时候代表接收到的是 bortli 压缩的数据包，这个时候要去解压。
    elif ver == 3:
        data = brotli.decompress(data[16:])
        await printDM(app, data, room_id)
        return

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    elif op == 5:
        jd = json.loads(data[16:].decode("utf-8", errors="ignore"))
        sstr = ""
        """
        if(jd['cmd'] == 'DANMU_MSG'):
            sstr = '[DANMU] ' + jd['info'][2][1] + ': ' + jd['info'][1]
        elif(jd['cmd'] == 'LIVE'):
            sstr = '[Notice] LIVE Start!'
        elif(jd['cmd'] == 'PREPARING'):
            sstr = '[Notice] LIVE Ended!'
        elif(jd['cmd'] == 'SEND_GIFT'):
            sstr = '[GIFT]' + jd['data']['uname'] + ' ' + jd['data']['action'] + \
                ' ' + str(jd['data']['num']) + 'x' + jd['data']['giftName']
        elif(jd['cmd'] == "INTERACT_WORD"):
            if jd['data']['msg_type'] == 1:
                sstr = '[ENTRY] ' + jd['data']['uname'] + ' 进入直播间'
            elif jd['data']['msg_type'] == 2:
                sstr = '[FOLLOW] ' + jd['data']['uname'] + ' 关注了直播间'
        elif(jd['cmd'] == "未知"):
            print(jd)
            sstr = '[SHARE] ' + jd['data']['uname'] + ' 分享了直播间'
        else:
            sstr = '[OTHER] ' + jd['cmd']

        if sstr != '':
            await app.send_group_message(group, MessageChain([Plain(sstr)]))
        """

        if jd["cmd"] != "LIVE":
            return
        logger.info(f"[NOTICE]: {room_id}: LIVE START!")
        Localpath = "./data/live.json"
        data = {}
        with open(Localpath, encoding="utf-8") as fr:
            data = json.load(fr)
            fr.close()
        info = get_info(room_id)
        for i in data["data"]:
            if room_id != str(i["room_id"]):
                continue
            for j in i["group"]:
                try:
                    sstr = f'{info["uname"]}的直播开始啦！\n直播间标题：{info["title"]}\n直播关键帧：'
                    await app.send_group_message(
                        j,
                        MessageChain(
                            [
                                Plain(sstr),
                                Image(url=info["keyframe"]),
                                Plain(
                                    "\n直播间地址：https://live.bilibili.com/%d"
                                    % info["room_id"]
                                ),
                            ]
                        ),
                    )
                except:
                    pass
            raise Exception("断开连接")


def get_info(room_id: str):
    """获取b站用户个人信息"""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    headers = {"user-Agent": user_agent}

    url = (
        "https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id=%s"
        % room_id
    )

    data_raw = requests.get(url, headers=headers).json()

    # uid = data_raw['data']['room_info']['uid']
    # room_id = data_raw['data']['room_info']['room_id']
    # title = data_raw['data']['room_info']['title']
    # keyframe = data_raw['data']['room_info']['keyframe']
    # uname = data_raw['data']['anchor_info']['base_info']['uname']

    # data = {'title': title,
    #         'user': uname,
    #         'uid': uid,
    #         'room_id': room_id,
    #         'keyframe': keyframe}
    if data_raw["code"] == 0:
        data = data_raw["data"]["room_info"]
        data["uname"] = data_raw["data"]["anchor_info"]["base_info"]["uname"]
    else:
        data = {"msg": "没有这个直播间"}
    return data


def livewrite(group: int, room_id: int):
    """写入json文件"""
    Localpath = "./data/live.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()

    for i in data["data"]:
        if i["room_id"] == room_id:
            l = i["group"]
            l.append(group)
            i["group"] = l
            break
    else:
        l = data["data"]
        n = {"room_id": room_id, "group": [group]}
        l.append(n)
        data["data"] = l
        pass

    with open(Localpath, "w", encoding="utf8") as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()
    pass
