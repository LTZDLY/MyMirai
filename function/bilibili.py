import datetime
import json
import time

import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Forward, ForwardNode, Image, Plain

from function.bilibili_private import draw_messages
from function.data import cookie, dancing_cookie, token

table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608


def dec(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]]*58**i
    return (r-add) ^ xor


async def sign(app, group):
    url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
    headers = {"cookie": cookie, "room_id": "330091",
               "csrf_token": token, "csrf": token}
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        await app.send_group_message(group, MessageChain([Plain("签到成功！本次签到奖励为：" + r.json()["data"]["text"])]))
        await app.send_group_message(group, MessageChain([Plain("本月一共签到" + str(r.json()["data"]["hadSignDays"]) + "天")]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))


async def get(app, group):
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "area_v2": "235", "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    addr = r.json()["data"]["rtmp"]["addr"]
    code = r.json()["data"]["rtmp"]["code"]
    if (r.json()["data"]["status"] == "LIVE"):
        await app.sendFriendMessage(349468958, MessageChain([Plain(addr)]))
        await app.sendFriendMessage(349468958, MessageChain([Plain(code)]))
        await app.send_group_message(group, MessageChain([Plain("直播间开启成功")]))
    else:
        await app.send_group_message(group, MessageChain([Plain("直播间开启失败，可能是cookie过期")]))


async def end(app, group):
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"
    headers = {"cookie": cookie}
    data = {"room_id": "330091", "csrf_token": token,
            "csrf": token, "platform": "pc"}
    r = requests.post(url, data, headers=headers)
    if (r.json()["data"]["status"] == "PREPARING"):
        await app.send_group_message(group, MessageChain([Plain("直播间关闭成功")]))


async def change(app, group, msg: str):
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
        await app.send_group_message(group, MessageChain([Plain("直播间标题已更改为：\n" + title)]))
    else:
        await app.send_group_message(group, MessageChain([Plain("直播间标题更改失败，可能是cookie过期")]))


async def triple(app, group, msg: str):
    text = msg.split(' ')
    if(len(text) < 2):
        return
    av = 0
    if text[1].startswith("av"):
        av = text[1].replace("av", "")
    elif text[1].startswith("AV"):
        av = text[1].replace("AV", "")
    elif text[1].startswith("BV") or text[1].startswith("bv"):
        av = dec(text[1])

    url = " https://api.bilibili.com/x/web-interface/archive/like/triple"
    headers = {"cookie": cookie}
    data = {"csrf": token, "aid": av}
    r = requests.post(url, data, headers=headers)
    if (r.json()["code"] == 0):
        await app.send_group_message(group, MessageChain([Plain("三连成功！")]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))


async def private_msg_init(app, group):
    Localpath = './data/bili_private.json'
    import os
    if os.path.exists(Localpath):
        return

    # 检测到文件不存在，首先进行初始化
    await app.send_group_message(group, MessageChain([Plain("检测到文件不存在，首先进行初始化")]))

    bili_private = {}
    headers = {"cookie": dancing_cookie}
    # 首先访问这个地址，获取所有的会话信息。
    url = 'https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&size=200'
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        session_list = (r.json()['data']['session_list'])

    # 然后访问这个地址，获取所有会话人的会话信息。
    for i in session_list:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id={i["talker_id"]}&session_type=1'
        r = requests.get(url, headers=headers)
        if (r.json()["code"] == 0):
            msg = r.json()['data']['messages']
            if not msg:
                continue
            bili_private[i["talker_id"]] = msg[0]['timestamp']

    with open(Localpath, "w") as fw:
        jsObj = json.dumps(bili_private)
        fw.write(jsObj)
        fw.close()

    await app.send_group_message(group, MessageChain([Plain(f"初始化结束，本次初始化共加载了{len(bili_private)}个人的通信信息。")]))


def private_msg(app):
    Localpath = './data/bili_private.json'
    with open(Localpath, 'r', encoding='utf8')as fp:
        bili_private = json.load(fp)

    # print(bili_private)
    headers = {"cookie": dancing_cookie}
    # 首先访问这个地址，获取所有的会话信息。
    url = 'https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&size=10'
    r = requests.get(url, headers=headers)
    if (r.json()["code"] == 0):
        session_list = (r.json()['data']['session_list'])
    else:
        return MessageChain([Plain(r.json()['message'])])

    # 然后访问这个地址，获取所有会话人的会话信息。
    msgs = {}
    for i in session_list:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id={i["talker_id"]}&session_type=1'
        r = requests.get(url, headers=headers)
        if (r.json()["code"] == 0):
            msg = r.json()['data']['messages']
            if not msg:
                continue
            if not str(i["talker_id"]) in bili_private:
                bili_private[str(i["talker_id"])] = 0
            # print(i["talker_id"], msg[0]['timestamp'], bili_private[str(i["talker_id"])])
            if msg[0]['timestamp'] != bili_private[str(i["talker_id"])]:
                tmsgs = []
                for j in msg:
                    if not str(j["sender_uid"]) in bili_private:
                        continue
                    if j['timestamp'] != bili_private[str(j["sender_uid"])]:
                        tmsgs.append(j)
                    else:
                        break
                msgs[i["talker_id"]] = tmsgs

            bili_private[str(i["talker_id"])] = msg[0]['timestamp']

    with open(Localpath, "w") as fw:
        jsObj = json.dumps(bili_private)
        fw.write(jsObj)
        fw.close()

    if msgs:
        return bili_private_handler(app, msgs)

    # print(len(msg), i['talker_id'])


def bili_private_handler(app, msgs):
    headers = {"cookie": dancing_cookie}
    msg_list = []
    num_people = 0
    num_message = 0
    for i in msgs:
        num_people += 1
        temp = {}
        # 访问这个地址，获取会话人的个人信息
        url = f'https://api.vc.bilibili.com/account/v1/user/cards?uids={i}'
        r = requests.get(url, headers=headers)
        if (r.json()["code"] == 0):
            data = r.json()['data'][0]
            temp['name'] = data['name']
            temp['face'] = data['face']
            ttemp = []
            tmsgs = msgs[i]
            for j in tmsgs:
                tttemp = {}
                tttemp['time'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S', time.localtime(j['timestamp']))
                num_message += 1
                if j["msg_type"] == 1:
                    tttemp["type"] = 'text'
                    tttemp["content"] = json.loads(j["content"])
                elif j["msg_type"] == 2:
                    tttemp["type"] = 'img'
                    tttemp["content"] = json.loads(j["content"])
                else:
                    tttemp["type"] = 'unknow'
                    tttemp["content"] = {"content": "[不支持的消息类型]"}
                ttemp.append(tttemp)
            temp['msgs'] = ttemp

            # msg = r.json()['data']['messages']
            # print(len(msg), i['talker_id'])
            pass
        if temp:
            msg_list.append(temp)

    print(msg_list)
    img_list = draw_messages(msg_list)

    fwd_nodeList = [
        ForwardNode(
            target=app.account,
            senderName='我',
            time=datetime.datetime.now(),
            message=MessageChain(
                [Plain(f"拉取消息结束，本次共拉取了{num_people}个人的共{num_message}条消息。")]),
        )
    ]

    for i in img_list:
        i.save('./source/bili_bak.png')
        fwd_nodeList.append(
            ForwardNode(
                target=app.account,
                senderName='我',
                time=datetime.datetime.now(),
                message=MessageChain(
                    [Image(path='./source/bili_bak.png')]),
            )
        )
    
    message = MessageChain(Forward(nodeList=fwd_nodeList))
    return message


async def bilibili(app, group, msg: str):
    if (msg == "bilibili.signup"):
        await sign(app, group)
    elif (msg == "bilibili.get"):
        await get(app, group)
    elif (msg == "bilibili.end"):
        await end(app, group)
    elif (msg.startswith("bilibili.change")):
        await change(app, group, msg)
    elif (msg.startswith("bilibili.triple")):
        await triple(app, group, msg)

# private_msg()
