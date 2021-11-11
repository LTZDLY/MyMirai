# 此为使用弹幕姬源码，可以直接运行使用。


import asyncio
import datetime
import json
import zlib

import aiohttp
import requests

remote = 'wss://tx-bj-live-comet-01.chat.bilibili.com/sub'

hb = '00000010001000010000000200000001'


def get_data(room_id):
    '''生成握手包数据'''
    # 获取token
    url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id=%s&type=0' % room_id
    r = requests.get(url)
    if (r.json()["code"] == 0):
        key = r.json()['data']['token']

    # 握手包数据内容
    data_json = {'uid': 0,
                 'roomid': int(room_id),
                 'protover': 2,
                 'platform': 'web',
                 'clientver': '2.6.41',
                 'type': 2,
                 'key': key}
    text = json.dumps(data_json)

    # 握手包数据头
    # 数据头长度为16，[0:4]为数据包长度，[5:6]为数据包头部长度，固定为16，[7:8]为协议版本，目前为1，
    # [9:12]为操作码，握手包为7代表认证并加入房间，[13:16]为sequence，可以取常数1

    # 对应为 长度[\x00\x00\x01\x02] 头部长度[\x00\x10] 协议版本[\x00\x01] 操作码[\x00\x00\x00\x07] sequence[\x00\x00\x00\x01]
    size = len(text) + 16  # 十进制下的数据包总长度
    bytesize = hex(size)[2:]  # 十六进制下的数据包总长度
    data_head = '0' * (8 - len(bytesize)) + bytesize + \
        '001000010000000700000001'  # 对长度补0并且将除了长度之后的内容进行拼接

    data_text = text.encode('ascii')  # 将数据包内容转为bytes型
    data = data_head + data_text.hex()  # 将数据包头和数据包内容进行拼接之后返回
    return bytes.fromhex(data)


async def entrence(room_id):
    '''弹幕服务器接入口'''
    await startup(room_id)
    num = 0
    while(True):
        num += 1
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
        t = t[:len(t) - 3] + ']'
        print('%s[ERROR]: %s: 连接断开，正在尝试第%d次重连.' % (t, room_id, num))
        await startup(room_id)


async def startup(room_id: str):
    '''创建ws连接b站弹幕服务器'''
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect(remote) as ws:
                await ws.send_bytes(get_data(room_id))
                asyncio.create_task(sendHeartBeat(ws, room_id))
                t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
                t = t[:len(t) - 3] + ']'
                print(session.closed)
                print('%s[NOTICE]: 开启对房间号%s的视奸' % (t, room_id))
                print(session.closed)
                await asyncio.sleep(60)
                async for msg in ws:
                    printDM(msg.data, room_id)
                print(session.closed)
        except Exception as e:
            print(e)
            print(e.args)


async def sendHeartBeat(websocket, room_id):
    '''每30秒发送心跳包'''
    while True:
        await asyncio.sleep(30)
        if websocket.closed:
            break  # 若连接断开，则退出函数
        await websocket.send_bytes(bytes.fromhex(hb))
        t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
        t = t[:len(t) - 3] + ']'
        print('%s[NOTICE]: %s: Sent HeartBeat.' % (t, room_id))

# 将数据包传入：


def printDM(data, room_id):
    '''解析并输出数据包的数据'''
    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，

    if(len(data) > packetLen):
        printDM(data[packetLen:], room_id)
        data = data[:packetLen]

    # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
    if(ver == 2):
        data = zlib.decompress(data[16:])
        printDM(data, room_id)
        return

    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    if(ver == 1):
        if(op == 3):
            t = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S,%f")
            t = t[:len(t) - 3] + ']'
            print('%s[POPULARITY]: %s: %d' %
                  (t, room_id, int(data[16:].hex(), 16)))
        return
    
    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    if(op == 5):
        jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
        print(jd)
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
            print(sstr)


if __name__ == "__main__":
    roomid = int(input('请输入房间号'))
    asyncio.get_event_loop().run_until_complete(startup(roomid))
