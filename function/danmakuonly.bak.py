# 此为使用弹幕姬源码，可以直接运行使用。
# 参考：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/message_stream.md

import asyncio
import datetime
import json
import zlib

import aiohttp
import brotli

# import speech
from function.logger import logger
from function.tools import decode_protobuf, get_data, hb

async def entrence(room_id):
    """弹幕服务器接入口"""
    num = 0
    while True:
        await startup(room_id)
        num += 1
        logger.info(f"[ERROR]: {room_id}: 连接断开，正在尝试第{num}次重连.")


async def startup(room_id: str):
    """创建ws连接b站弹幕服务器"""
    async with aiohttp.ClientSession() as session:
        logger.info("aiohttp.ClientSession() as session")
        remote, handshake = get_data(room_id)
        try:
            async with session.ws_connect(remote) as ws:
                logger.info("async with session.ws_connect(remote) as ws:")
                await ws.send_bytes(handshake)
                task = asyncio.create_task(sendHeartBeat(ws, room_id))
                logger.info(f"[NOTICE]: 开启对房间号{room_id}的视奸")
                logger.info(f"{session}, {id(session)}")
                logger.info(f"{ws}, {id(ws)}")
                while True:
                    msg = await ws.receive()
                    logger.info("new message")
                    printDM(msg.data, room_id)

        except Exception as e:
            if str(e) == "断开连接":
                logger.info("断开连接")
                await ws.close()
                # await asyncio.sleep(270)
            else:
                raise e
            await asyncio.sleep(10)


async def sendHeartBeat(websocket, room_id):
    """每30秒发送心跳包"""
    while True:
        await asyncio.sleep(30)
        if websocket.closed:
            logger.info(f"[NOTICE]: {room_id}: HeartBeat Break.")
            break  # 若连接断开，则退出函数
        await websocket.send_bytes(bytes.fromhex(hb))
        logger.info(f"[NOTICE]: {room_id}: Sent HeartBeat.")


# 将数据包传入：


def printDM(data, room_id, ws=None):
    if ws:
        logger.info(f"{ws, id(ws)}")
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
        printDM(data[packetLen:], room_id)
        data = data[:packetLen]

    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    if ver == 1:
        if op == 3:
            t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f]")
            logger.info(f"{t}[RENQI] {int(data[16:].hex(), 16)}")
            pass

    # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
    elif ver == 2:
        data = zlib.decompress(data[16:])
        printDM(data, room_id)
        return

    elif ver == 3:
        data = brotli.decompress(data[16:])
        printDM(data, room_id)
        return

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    if op == 5:
        jd = json.loads(data[16:].decode("utf-8", errors="ignore"))
        # print(jd)
        sstr = ""
        if jd["cmd"] == "DANMU_MSG":
            sstr = "[DANMU] " + jd["info"][2][1] + ": " + jd["info"][1]
            # speech.say(f"{jd['info'][2][1]}说，{jd['info'][1]}")
        elif jd["cmd"] == "LIVE":
            sstr = "[Notice] LIVE Start!"
            # speech.say("直播已开始")
        elif jd["cmd"] == "PREPARING":
            sstr = "[Notice] LIVE Ended!"
            # speech.say("直播已结束")
        elif jd["cmd"] == "SEND_GIFT":
            sstr = (
                "[GIFT]"
                + jd["data"]["uname"]
                + " "
                + jd["data"]["action"]
                + " "
                + str(jd["data"]["num"])
                + "x"
                + jd["data"]["giftName"]
            )
        elif jd["cmd"] == "INTERACT_WORD":
            if jd["data"]["msg_type"] == 1:
                sstr = "[ENTRY] " + jd["data"]["uname"] + " 进入直播间"
            elif jd["data"]["msg_type"] == 2:
                sstr = "[FOLLOW] " + jd["data"]["uname"] + " 关注了直播间"
            elif jd["cmd"] == "INTERACT_WORD_V2":
                # data.pb 为 base64 编码的 protobuf（无公开 schema），解码后放回 json
                try:
                    jd["data"]["pb"] = decode_protobuf(jd["data"]["pb"])
                except Exception as e:
                    print(f"[WARN] pb 解码失败: {e}")
                pb = jd["data"].get("pb") or {}
                # 与旧版 INTERACT_WORD 字段对应：field_1=uid field_2=uname field_5=msg_type
                if isinstance(pb, dict):
                    uid = pb.get("field_1")
                    uname = pb.get("field_2")
                    msg_type = pb.get("field_5")
                    if msg_type == 1:
                        sstr = f"[ENTRY] {uname}({uid}) 进入直播间"
                    elif msg_type == 2:
                        sstr = "[FOLLOW] " + str(uname) + " 关注了直播间"
        elif jd["cmd"] == "未知":
            logger.info(jd)
            sstr = "[SHARE] " + jd["data"]["uname"] + " 分享了直播间"
        else:
            sstr = "[OTHER] " + jd["cmd"]

        if sstr != "":
            logger.info(sstr)

        if jd["cmd"] == "LIVE" or (
            jd["cmd"] == "INTERACT_WORD" and jd["data"]["msg_type"] == 1
        ):
            raise Exception("断开连接")

    else:
        logger.info(data)


if __name__ == "__main__":
    roomid = int(input("请输入房间号"))
    asyncio.run(entrence(roomid))
