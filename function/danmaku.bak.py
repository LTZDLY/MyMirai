import asyncio
import json
import zlib

import aiohttp
import brotli
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain

from function.logger import logger
from function.bilibili import get_info, danmu_group
from function.tools import get_data, hb

async def entrence(app, room_id):
    """弹幕服务器接入口"""
    num = 0
    while True:
        await startup(app, room_id)
        num += 1
        logger.info(f"[ERROR]: {room_id}: 连接断开，正在尝试第{num}次重连.")


async def startup(app, room_id: str):
    """创建ws连接b站弹幕服务器"""
    async with aiohttp.ClientSession() as session:
        remote, handshake = get_data(room_id)
        async with session.ws_connect(remote) as ws:
            await ws.send_bytes(handshake)
            asyncio.create_task(sendHeartBeat(ws, room_id))
            logger.info(f"[NOTICE]: 开启对房间号{room_id}的视奸")
            try:
                async for msg in ws:
                    await printDM(app, msg.data, room_id)
            except Exception as e:
                if str(e) == "断开连接":
                    logger.info(f"{room_id}: 断开连接")
                    await ws.close()
                    await asyncio.sleep(270)
                else:
                    raise e
                await asyncio.sleep(30)


async def sendHeartBeat(websocket, room_id):
    """每30秒发送心跳包"""
    while True:
        await asyncio.sleep(30)
        if websocket.closed:
            # logger.info(f"[NOTICE]: {room_id}: HeartBeat Break.")
            break  # 若连接断开，则退出函数
        await websocket.send_bytes(bytes.fromhex(hb))
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
    if op == 5:
        jd = json.loads(data[16:].decode("utf-8", errors="ignore"))
        sstr = ""
        # if(jd['cmd'] == 'DANMU_MSG'):
        #     sstr = '[DANMU] ' + jd['info'][2][1] + ': ' + jd['info'][1]
        # elif(jd['cmd'] == 'LIVE'):
        #     sstr = '[Notice] LIVE Start!'
        # elif(jd['cmd'] == 'PREPARING'):
        #     sstr = '[Notice] LIVE Ended!'
        # elif(jd['cmd'] == 'SEND_GIFT'):
        #     sstr = '[GIFT]' + jd['data']['uname'] + ' ' + jd['data']['action'] + \
        #         ' ' + str(jd['data']['num']) + 'x' + jd['data']['giftName']
        # elif(jd['cmd'] == "INTERACT_WORD"):
        #     if jd['data']['msg_type'] == 1:
        #         sstr = '[ENTRY] ' + jd['data']['uname'] + ' 进入直播间'
        #     elif jd['data']['msg_type'] == 2:
        #         sstr = '[FOLLOW] ' + jd['data']['uname'] + ' 关注了直播间'
        # elif(jd['cmd'] == "未知"):
        #     print(jd)
        #     sstr = '[SHARE] ' + jd['data']['uname'] + ' 分享了直播间'
        # else:
        #     sstr = '[OTHER] ' + jd['cmd']

        # if sstr != '':
        #     await app.send_group_message(group, MessageChain([Plain(sstr)]))

        if jd["cmd"] == "DANMU_MSG":
            groups = danmu_group.get(str(room_id), [])
            if groups:
                sstr = "[弹幕] " + jd["info"][2][1] + ": " + jd["info"][1]
                for j in groups:
                    try:
                        await app.send_group_message(j, MessageChain([Plain(sstr)]))
                    except:
                        pass
            return

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
