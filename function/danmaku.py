import asyncio
import json
import zlib
import base64

from aiowebsocket.converses import AioWebSocket
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

roomid = '22428702'

remote = 'wss://tx-bj-live-comet-01.chat.bilibili.com/sub'

hb = '00000010001000010000000200000001'
async def startup(app, group, roomid: str):
    #FIXME B站弹幕服务器又搞什么幺蛾子了原本的连接方法失效且不明白是为什么，初步怀疑是现在不再接受过少的参数
    data_raw = '000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
    data_raw = data_raw.format(headerLen=hex(
        27+len(roomid))[2:], roomid=''.join(map(lambda x: hex(ord(x))[2:], list(roomid))))
    try:
        async with AioWebSocket(remote) as aws:
            converse = aws.manipulator
            print(bytes.fromhex(data_raw))
            print(base64.b64encode(bytes.fromhex(data_raw)))
            print(base64.b64decode("AAABAgAQAAEAAAAHAAAAAXsidWlkIjo4MDEyNDE4LCJyb29taWQiOjIxNjc3OTY5LCJwcm90b3ZlciI6MiwicGxhdGZvcm0iOiJ3ZWIiLCJjbGllbnR2ZXIiOiIyLjQuMTYiLCJ0eXBlIjoyLCJrZXkiOiI5VkoyaDZpV05tWXR0V1hvdElPcVF3YU5ldUZaQnJPMjJQRk1sYTJkTnlkRGxaa21mcnJnNnFEby1qYmhqam1tT1JTV25ncVVXRzBTOXBiM3BzRmtNaGJxXzRFQUhNa2N5LUxhcl9WRGU2dFpWQjA1SEE4a0h5UHcyVEZGTzJYckt0UHI0QnRFRFM0PSJ9"))
            await converse.send(bytes.fromhex(data_raw))

            data = await converse.receive()
            print(data)

            jd = json.loads(
                data[16:].decode('utf-8', errors='ignore'))
            if jd['code'] != 0:
                return
            await app.sendGroupMessage(group, MessageChain.create([Plain("直播间连接成功")]))
            tasks = [receDM(app, group, converse), sendHeartBeat(converse)]
            await asyncio.wait(tasks)

    except Exception as e:
        await app.sendGroupMessage(group, MessageChain.create([Plain("直播间连接关闭")]))
        pass


async def sendHeartBeat(websocket):
    while True:
        await asyncio.sleep(30)
        await websocket.send(bytes.fromhex(hb))
        print('[Notice] Sent HeartBeat.')


async def receDM(app, group, websocket):
    while True:
        recv_text = await websocket.receive()
        await (printDM(app, group, recv_text))

# 将数据包传入：


async def printDM(app, group, data):
    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，

    if(len(data) > packetLen):
        asyncio.create_task(printDM(app, group, data[packetLen:]))
        data = data[:packetLen]

    # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
    if(ver == 2):
        data = zlib.decompress(data[16:])
        asyncio.create_task(printDM(app, group, data))
        return

    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    if(ver == 1):
        if(op == 3):
            print('[RENQI]  {}'.format(int(data[16:].hex(), 16)))
        return

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    if(op == 5):
        try:
            jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
            sstr = ''
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
                await app.sendGroupMessage(group, MessageChain.create([Plain(sstr)]))
        except Exception as e:
            pass


async def danmaku(app, group, roomid):
    await startup(app, group, roomid)
    pass

if __name__ == '__main__':
    try:
        print(base64.b64decode("AAAA+AAQAAEAAAAHAAAAAXsidWlkIjowLCJyb29taWQiOjIxNjc3OTY5LCJwcm90b3ZlciI6MiwicGxhdGZvcm0iOiJ3ZWIiLCJjbGllbnR2ZXIiOiIyLjQuMTYiLCJ0eXBlIjoyLCJrZXkiOiJNWThXY1VjSl9UZVJrR3U3QV9DVEM3RmZLcDZmZDlMaWZiYV9sTkR0azVxMDdOTE1RaktSb3Y3SnVPWEFCd2p5OXowQl85OVNPczRtQ19nZVJpbGRUSklCT2xCbTctUmM2M2xJN05DZjVyZWRYYXBkbmdjX0NmbkVRVnJYb014Q1pYX243QT09In0="))
        s = str("type:2")
        print(s.encode('utf-8'))
        pass
    except KeyboardInterrupt as exc:
        print("Quit.")
