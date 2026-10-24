# 此为使用另一库实现的弹幕姬源码，可以直接运行使用。
# 因原库在服务器上运行时会有不明原因导致失败，故寻找另一库重新实现该功能，效果良好
# 参考：https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/message_stream.md

import asyncio
import datetime
import json
import zlib

import brotli

# import speech
from aiowebsocket.converses import AioWebSocket

from logger import logger

from function.tools import decode_protobuf, get_data, hb

async def startup(room_id: str):
    remote, d = get_data(room_id)
    async with AioWebSocket(remote) as aws:
        converse = aws.manipulator
        await converse.send(d)
        tasks = asyncio.create_task(sendHeartBeat(aws, room_id))
        # try:
        while True:
            if converse.message_queue.full():
                break
            recv_text = await converse.receive()
            # print(recv_text)
            printDM(recv_text)
        # except Exception as e:
        #     tasks.cancel()
        #     if str(e) == "断开连接":
        #         logger.info("断开连接")
        #         await aws.close_connection()
        #         tasks.cancel()

        #         # await asyncio.sleep(300)
        #     await asyncio.sleep(10)


async def sendHeartBeat(websocket: AioWebSocket, room_id):
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
                        sstr += f"[ENTRY] {uname}({uid}) 进入直播间"
                    elif msg_type == 2:
                        sstr += "[FOLLOW] " + str(uname) + " 关注了直播间"
            elif jd["cmd"] == "未知":
                print(jd)
                sstr += "[SHARE] " + jd["data"]["uname"] + " 分享了直播间"
            else:
                sstr += "[OTHER] " + jd["cmd"]
                pass

            if sstr != "":
                print(sstr)

        # if jd["cmd"] == "LIVE" or (
        #     jd["cmd"] == "INTERACT_WORD" and jd["data"]["msg_type"] == 1
        # ):
        #     raise Exception("断开连接")

    else:
        print(data)


if __name__ == "__main__":
    roomid = int(input("请输入房间号"))
    asyncio.run(startup(roomid))
