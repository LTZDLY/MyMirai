# 此为使用另一库实现的直播监听功能代码。
# 因原库在服务器上运行时会有不明原因导致失败，故寻找另一库重新实现该功能，效果良好


import asyncio
import datetime
import json
import zlib

import brotli
from aiowebsocket.converses import AioWebSocket
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain

from function.bilibili import get_info, danmu_group
from function.tools import get_data, hb

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
    remote, d = get_data(room_id)
    async with AioWebSocket(remote) as aws:
        converse = aws.manipulator
        await converse.send(d)
        tasks = asyncio.create_task(sendHeartBeat(converse, room_id))
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
        t = t[: len(t) - 3] + "]"
        print("%s[NOTICE]: 开启对房间号%s的视奸" % (t, room_id))
        flag = True
        while flag:
            recv_text = await converse.receive()
            flag = await printDM(app, recv_text, room_id)
        tasks.cancel()
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
        return True

    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
    if len(data) > packetLen:
        f1 = await printDM(app, data[packetLen:], room_id)
        f2 = await printDM(app, data[:packetLen], room_id)
        return bool(f1 and f2)

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
        return await printDM(app, data, room_id)

    # ver 为3的时候代表接收到的是 bortli 压缩的数据包，这个时候要去解压。
    elif ver == 3:
        data = brotli.decompress(data[16:])
        return await printDM(app, data, room_id)

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    elif ver == 0:
        if op == 5:
            jd = json.loads(data[16:].decode("utf-8", errors="ignore"))
            t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
            t = t[: len(t) - 3] + "]"
            sstr = t
            # if jd["cmd"] == "DANMU_MSG":
            #     sstr += f"[DANMU] {jd['info'][2][1]}: {jd['info'][1]}"
            #     # speech.say(f"{jd['info'][2][1]}说，{jd['info'][1]}")
            # elif jd["cmd"] == "LIVE":
            #     sstr += "[Notice] LIVE Start!"
            #     # speech.say("直播已开始")
            # elif jd["cmd"] == "PREPARING":
            #     sstr += "[Notice] LIVE Ended!"
            #     # speech.say("直播已结束")
            # elif jd["cmd"] == "SEND_GIFT":
            #     sstr += (
            #         "[GIFT]"
            #         + jd["data"]["uname"]
            #         + " "
            #         + jd["data"]["action"]
            #         + " "
            #         + str(jd["data"]["num"])
            #         + "x"
            #         + jd["data"]["giftName"]
            #     )
            #     # speech.say(f"感谢{jd['data']['uname']}赠送的{jd['data']['num']}个{jd['data']['giftName']}")
            # elif jd["cmd"] == "INTERACT_WORD":
            #     if jd["data"]["msg_type"] == 1:
            #         # print(jd['data'])
            #         sstr += f"[ENTRY] {jd['data']['uname']}({jd['data']['uid']}) 进入直播间"
            #         # speech.say(f"欢迎{jd['data']['uname']}进入直播间")
            #     elif jd["data"]["msg_type"] == 2:
            #         sstr += "[FOLLOW] " + jd["data"]["uname"] + " 关注了直播间"
            # elif jd["cmd"] == "未知":
            #     print(jd)
            #     sstr += "[SHARE] " + jd["data"]["uname"] + " 分享了直播间"
            # else:
            #     sstr += "[OTHER] " + jd["cmd"]
            #     pass

            # if sstr != "":
            #     await app.send_group_message(581833643, MessageChain([Plain(sstr)]))
            if jd["cmd"] == "DANMU_MSG":
                groups = danmu_group.get(str(room_id), [])
                if groups:
                    for j in groups:
                        try:
                            sstr += "[弹幕] " + jd["info"][2][1] + ": " + jd["info"][1]
                            await app.send_group_message(j, MessageChain([Plain(sstr)]))
                        except:
                            pass
                return True

            if jd["cmd"] != "LIVE":
                return True
            print("%s[NOTICE]: %s: LIVE START!" % (t, room_id))
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
            return False
    return True
