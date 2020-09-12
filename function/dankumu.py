from mirai import Mirai, Plain, MessageChain, Friend, Group, GroupMessage, FriendMessage, MessageChain
import asyncio
import zlib
from aiowebsocket.converses import AioWebSocket
import json
import helloworld
import ini
from multiprocessing import Process

global roomid
global data_raw


async def startup(url, roomid):
    data_raw='000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
    data_raw=data_raw.format(headerLen=hex(27+len(roomid))[2:], roomid=''.join(map(lambda x:hex(ord(x))[2:],list(roomid))))
    async with AioWebSocket(url) as aws:
        converse = aws.manipulator
        data = bytes.fromhex(data_raw)
        data = b'\x00\x00\x00\x20\x00\x10\x00\x01\x00\x00\x00\x07\x00\x00\x00\x01{"roomid"=11928}'
        msgg = str(data)
        print(data_raw)
        print(data)
        packetLen = int(data[:4].hex(),16)
        dataLen = int(data[4:6].hex(),16)
        ver = int(data[6:8].hex(),16)
        op = int(data[8:12].hex(),16)
        headLen = int(data[12:16].hex(),16)
        text = data[16:].decode('utf-8', errors='ignore')
        print(packetLen)
        print(dataLen)
        print(ver)
        print(op)
        print(headLen)
        print(text)
        await converse.send(msgg)
        tasks=[receDM(converse), sendHeartBeat(converse)]
        await asyncio.wait(tasks)

hb = '00000010001000010000000200000001'
async def sendHeartBeat(websocket):
    while True:
        await asyncio.sleep(30)
        await websocket.send(bytes.fromhex(hb))
        print('[Notice] Sent HeartBeat.')

async def receDM(websocket):
    while True:
        recv_text = await websocket.receive()
        printDM(recv_text)


# 将数据包传入：
def printDM(data):
    # 获取数据包的长度，版本和操作类型
    packetLen = int(data[:4].hex(),16)
    ver = int(data[6:8].hex(),16)
    op = int(data[8:12].hex(),16)

    # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
    '''
    if(len(data)>packetLen):
        printDM(data[packetLen:])
        data=data[:packetLen]
    '''


    # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
    if(ver == 2):
        data = zlib.decompress(data[16:])
        printDM(data)
        return
    
    # ver 为1的时候为进入房间后或心跳包服务器的回应。op 为3的时候为房间的人气值。
    if(ver == 1):
        if(op == 3):
            print('[RENQI]  {}'.format(int(data[16:].hex(),16)))
        return

    # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
    # op 为5意味着这是通知消息，cmd 基本就那几个了。
    if(op==5):
        try:
            jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
            '''
            if(jd['cmd']=='LIVE'):
                print('[Notice] LIVE Start!')
            elif(jd['cmd']=='PREPARING'):
                print('[Notice] LIVE Ended!')
            '''
            if(jd['cmd']=='DANMU_MSG'):
                print('[DANMU] ', jd['info'][2][1], ': ', jd['info'][1])
                msg = '[DANMU] ' + jd['info'][2][1] + ': ' + jd['info'][1]
                print(msg)
            elif(jd['cmd']=='SEND_GIFT'):
                print('[GITT]',jd['data']['uname'], ' ', jd['data']['action'], ' ', jd['data']['num'], 'x', jd['data']['giftName'])
            elif(jd['cmd']=='LIVE'):
                print('[Notice] LIVE Start!')
            elif(jd['cmd']=='PREPARING'):
                print('[Notice] LIVE Ended!')
            else:
                print('[OTHER] ', jd['cmd'])
            
        except Exception as e:
            pass
        
        # await helloworld.app.sendFriendMessage(349468958, msg)

def liveaction(remote, roomid):
    asyncio.get_event_loop().run_until_complete(startup(remote, roomid))



def livestart():
    '''
    if os.path.exists('live.ini') == False:
        open('live.ini','w')

    config = configparser.ConfigParser()
    config.readfp(open('live.ini'))

    if ('Global' in config == False):
        config.add_section('Global')

    num = int(config.get("Global", "num", fallback = 0))
    '''
    num = int(ini.read_from_ini('live.ini', 'Global', 'num', '0'))
    pro = []
    for i in range(0, num):
        roomid = ini.read_from_ini('live.ini', 'Global', str(i), '0')
        remote = 'wss://broadcastlv.chat.bilibili.com:2245/sub'
        pro.append(Process(target = liveaction, args = (remote, roomid)))
        pro[i].start()
        # liveaction(remote, roomid)

if __name__ == "__main__":
    livestart()
    # helloworld.app.run()
    