import datetime
import json
import os
import time
from functools import partial
from io import BytesIO

import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Forward, ForwardNode, Image, Plain

from function.bilibili_private import draw_messages
from function.bilibili_qrlogin import bilibili_qrlogin
from function.data import gravity_bili_jct, gravity_cookie

table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608


def dec(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58**i
    return (r - add) ^ xor


async def sign(app, group):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    url = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
    headers = {
        "cookie": data["shinoai"]["cookie"],
        "room_id": "330091",
        "csrf_token": data["shinoai"]["bili_jct"],
        "csrf": data["shinoai"]["bili_jct"],
    }
    r = requests.get(url, headers=headers)
    if r.json()["code"] == 0:
        await app.send_group_message(
            group, MessageChain([Plain("签到成功！本次签到奖励为：" + r.json()["data"]["text"])])
        )
        await app.send_group_message(
            group,
            MessageChain(
                [Plain("本月一共签到" + str(r.json()["data"]["hadSignDays"]) + "天")]
            ),
        )
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))


async def get(app, group):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {"cookie": data["shinoai"]["cookie"]}
    data = {
        "room_id": "330091",
        "csrf_token": data["shinoai"]["bili_jct"],
        "csrf": data["shinoai"]["bili_jct"],
        "area_v2": "235",
        "platform": "pc",
    }
    r = requests.post(url, data, headers=headers)
    addr = r.json()["data"]["rtmp"]["addr"]
    code = r.json()["data"]["rtmp"]["code"]
    if r.json()["data"]["status"] == "LIVE":
        await app.sendFriendMessage(349468958, MessageChain([Plain(addr)]))
        await app.sendFriendMessage(349468958, MessageChain([Plain(code)]))
        await app.send_group_message(group, MessageChain([Plain("直播间开启成功")]))
    else:
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间开启失败，原因：\n{r.json()['message']}")])
        )


async def end(app, group):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"
    headers = {"cookie": data["shinoai"]["cookie"]}
    data = {
        "room_id": "330091",
        "csrf_token": data["shinoai"]["bili_jct"],
        "csrf": data["shinoai"]["bili_jct"],
        "platform": "pc",
    }
    r = requests.post(url, data, headers=headers)
    if r.json()["data"]["status"] == "PREPARING":
        await app.send_group_message(group, MessageChain([Plain("直播间关闭成功")]))


async def change(app, group, msg: str):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    text = msg.split(" ")
    if len(text) < 2:
        return
    title = text[1]
    if len(title) > 20:
        await app.send_group_message(group, MessageChain([Plain("标题过长，请更改")]))
        return
    for i in range(2, len(text)):
        title = title + " " + text[i]

    url = "https://api.live.bilibili.com/room/v1/Room/update"
    headers = {"cookie": data["shinoai"]["cookie"]}
    data = {
        "room_id": "330091",
        "csrf_token": data["shinoai"]["bili_jct"],
        "csrf": data["shinoai"]["bili_jct"],
        "title": title,
    }
    r = requests.post(url, data, headers=headers)
    if r.json()["msg"] == "ok":
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间标题已更改为：\n{title}")])
        )
    else:
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间标题更改失败，原因：\n{r.json()['message']}")])
        )


async def triple(app, group, msg: str):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    text = msg.split(" ")
    if len(text) < 2:
        return
    av = 0
    if text[1].startswith("av"):
        av = text[1].replace("av", "")
    elif text[1].startswith("AV"):
        av = text[1].replace("AV", "")
    elif text[1].startswith("BV") or text[1].startswith("bv"):
        av = dec(text[1])

    url = " https://api.bilibili.com/x/web-interface/archive/like/triple"
    headers = {"cookie": data["shinoai"]["cookie"]}
    data = {"csrf": data["shinoai"]["bili_jct"], "aid": av}
    r = requests.post(url, data, headers=headers)
    if r.json()["code"] == 0:
        await app.send_group_message(group, MessageChain([Plain("三连成功！")]))
    else:
        await app.send_group_message(group, MessageChain([Plain(r.json()["message"])]))


async def private_msg_init(app, tcookie):
    Localpath = f"./data/bili_private_{tcookie['name']}.json"
    # import os
    # if os.path.exists(Localpath):
    #     return

    # # 检测到文件不存在，首先进行初始化
    # await app.send_group_message(tcookie['group'], MessageChain([Plain(f"检测到{tcookie['name']}文件不存在，首先进行初始化")]))

    bili_private = {}
    headers = {"cookie": tcookie["cookie"]}
    # 首先访问这个地址，获取所有的会话信息。
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&size=200"
    r = requests.get(url, headers=headers)
    if r.json()["code"] == 0:
        session_list = r.json()["data"]["session_list"]

    # 然后访问这个地址，获取所有会话人的会话信息。
    for i in session_list:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id={i["talker_id"]}&session_type=1'
        r = requests.get(url, headers=headers)
        if r.json()["code"] == 0:
            msg = r.json()["data"]["messages"]
            if not msg:
                continue
            bili_private[i["talker_id"]] = msg[0]["timestamp"]

    with open(Localpath, "w", encoding="utf8") as fw:
        jsObj = json.dumps(bili_private)
        fw.write(jsObj)
        fw.close()

    await app.send_group_message(
        tcookie["group"],
        MessageChain([Plain(f"初始化结束，本次初始化共加载了{len(bili_private)}个人的通信信息。")]),
    )


def bili_priv_init(group, cookies):
    temp = {}
    temp["name"] = group
    temp["group"] = 0
    temp["bili_jct"] = ""
    temp["SESSDATA"] = ""
    temp["cookie"] = ""

    cookies["settings"][group] = 0
    cookies[group] = temp


async def getprivate(app, part):
    # part 此处代表部门名
    Localpath = "./data/cookies.json"
    with open(Localpath, "r", encoding="utf8") as fp:
        cookies = json.load(fp)
    data = cookies[part]
    print(f"{part}正在进行消息拉取...")
    msg = await private_msg(app, data)
    if msg:
        await app.send_group_message(data["group"], msg)
    else:
        print(f"{part}并没有拉取到东西")


async def private_msg(app, tcookie):
    Localpath = f"./data/bili_private_{tcookie['name']}.json"

    if not os.path.exists(Localpath):
        # 检测到文件不存在，首先进行初始化
        await app.send_group_message(tcookie['group'], MessageChain([Plain(f"检测到{tcookie['name']}文件不存在，首先进行初始化")]))
        await private_msg_init(app, tcookie)
        return

    with open(Localpath, "r", encoding="utf8") as fp:
        bili_private = json.load(fp)

    # print(bili_private)
    headers = {"cookie": tcookie["cookie"]}
    # 首先访问这个地址，获取所有的会话信息。
    url = "https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions?session_type=1&size=10"
    r = requests.get(url, headers=headers)
    if r.json()["code"] == 0:
        session_list = r.json()["data"]["session_list"]
    else:
        return MessageChain([Plain(r.json()["message"])])

    # 然后访问这个地址，获取所有会话人的会话信息。
    msgs = {}
    for i in session_list:
        url = f'https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs?talker_id={i["talker_id"]}&session_type=1'
        r = requests.get(url, headers=headers)
        if r.json()["code"] == 0:
            msg = r.json()["data"]["messages"]
            if not msg:
                continue
            if not str(i["talker_id"]) in bili_private:
                bili_private[str(i["talker_id"])] = 0
            # print(i["talker_id"], msg[0]['timestamp'], bili_private[str(i["talker_id"])])
            if msg[0]["timestamp"] != bili_private[str(i["talker_id"])]:
                tmsgs = []
                for j in msg:
                    if str(j["sender_uid"]) == str(tcookie['uid']):
                        tmsgs.append(j)
                    if not str(j["sender_uid"]) in bili_private:
                        continue
                    if j["timestamp"] != bili_private[str(j["sender_uid"])]:
                        tmsgs.append(j)
                    else:
                        break
                msgs[i["talker_id"]] = tmsgs

            bili_private[str(i["talker_id"])] = msg[0]["timestamp"]

    with open(Localpath, "w", encoding="utf8") as fw:
        jsObj = json.dumps(bili_private)
        fw.write(jsObj)
        fw.close()

    if msgs:
        return bili_private_handler(app, msgs, tcookie)

    # print(len(msg), i['talker_id'])


def bili_private_handler(app, msgs, tcookie):
    headers = {"cookie": tcookie["cookie"]}

    url = f"https://api.vc.bilibili.com/account/v1/user/cards?uids={tcookie['uid']}"
    r = requests.get(url, headers=headers)
    if r.json()["code"] == 0:
        face = r.json()["data"][0]
    

    msg_list = []
    num_people = 0
    num_message = 0
    for i in msgs:
        num_people += 1
        temp = {}
        temp['myface'] = face["face"]
        # 访问这个地址，获取会话人的个人信息
        url = f"https://api.vc.bilibili.com/account/v1/user/cards?uids={i}"
        r = requests.get(url, headers=headers)
        if r.json()["code"] == 0:
            if not r.json()["data"]:
                continue
            data = r.json()["data"][0]
            temp["name"] = data["name"]
            temp["face"] = data["face"]
            ttemp = []
            tmsgs = msgs[i]
            for j in tmsgs:
                tttemp = {}
                if j['sender_uid'] == tcookie['uid']:
                    tttemp["sender"] = 1
                tttemp["time"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(j["timestamp"])
                )
                num_message += 1
                if j["msg_type"] == 1:
                    tttemp["type"] = "text"
                    tttemp["content"] = json.loads(j["content"])
                elif j["msg_type"] == 2:
                    tttemp["type"] = "img"
                    tttemp["content"] = json.loads(j["content"])
                elif j["msg_type"] == 7:
                    tttemp["type"] = "video"
                    tttemp["content"] = json.loads(j["content"])
                else:
                    tttemp["type"] = "unknow"
                    tttemp["content"] = {"content": "[不支持的消息类型]"}
                ttemp.append(tttemp)
            temp["msgs"] = ttemp

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
            senderName="我",
            time=datetime.datetime.now(),
            message=MessageChain(
                [Plain(f"拉取消息结束，本次共拉取了{num_people}个人的共{num_message}条消息。")]
            ),
        )
    ]

    for i in img_list:
        img_bytes = BytesIO()
        i.save(img_bytes, format="PNG")
        i.close()
        fwd_nodeList.append(
            ForwardNode(
                target=app.account,
                senderName="我",
                time=datetime.datetime.now(),
                message=MessageChain(Image(data_bytes=img_bytes.getvalue())),
            )
        )

    message = MessageChain(Forward(nodeList=fwd_nodeList))
    return message


async def login(app, group, msg: str, mytasks):
    n = False
    text = msg.split(" ", 1)
    if len(text) < 2:
        await app.send_group_message(group, MessageChain([Plain("缺少参数")]))
        return
    part = text[1]

    Localpath = "./data/cookies.json"
    with open(Localpath, "r", encoding="utf8") as fp:
        cookies = json.load(fp)

    if not part in cookies["settings"]:
        n = True
        await app.send_group_message(
            group, MessageChain([Plain("没有该部门的登录记录，现在创建新的登录记录。")])
        )
        # cookies['settings'][part] = 1
    await app.send_group_message(
        group, MessageChain([Plain(f"您现在正在对{part}进行二维码登录，请使用已登录该账号的B站客户端扫描二维码完成登录")])
    )

    f, get_cookies = await bilibili_qrlogin(app, group)

    # 保存cookie
    if f:
        bj = requests.utils.dict_from_cookiejar(get_cookies)["bili_jct"]
        sd = requests.utils.dict_from_cookiejar(get_cookies)["SESSDATA"]
        uid = requests.utils.dict_from_cookiejar(get_cookies)["DedeUserID"]

        if n:
            temp = {}
            temp["uid"] = int(uid)
            temp["name"] = part
            temp["group"] = group.id
            temp["bili_jct"] = bj
            temp["SESSDATA"] = sd
            temp["cookie"] = f"SESSDATA={sd}; bili_jct={bj}"
            cookies[part] = temp
        else:
            cookies[part]["bili_jct"] = bj
            cookies[part]["SESSDATA"] = sd
            cookies[part]["cookie"] = f"SESSDATA={sd}; bili_jct={bj}"

        with open(Localpath, "w", encoding="utf8") as fw:
            jsObj = json.dumps(cookies)
            fw.write(jsObj)
            fw.close()

        # await private_msg_init(app, temp)
        if n:
            await getprivate(app, part)
            mytasks[part] = partial(getprivate, app, part)


async def bilibili(app, group, msg: str):
    if msg == "bilibili.signup":
        await sign(app, group)
    elif msg == "bilibili.get":
        await get(app, group)
    elif msg == "bilibili.end":
        await end(app, group)
    elif msg.startswith("bilibili.change"):
        await change(app, group, msg)
    elif msg.startswith("bilibili.triple"):
        await triple(app, group, msg)


async def bilibili_group(app, mytasks, group, msg: str):
    if msg.startswith("bilibili.login"):
        await login(app, group, msg, mytasks)
    # if (msg.startswith("bilibili.createtask")):
    #     await createtask(app, mytasks, group, msg)


# private_msg()


async def get_gravity(app, group, member):
    url = "https://api.live.bilibili.com/room/v1/Room/startLive"
    headers = {"cookie": gravity_cookie}
    data = {
        "room_id": "1925638",
        "csrf_token": gravity_bili_jct,
        "csrf": gravity_bili_jct,
        "area_v2": "255",
        "platform": "pc",
    }  # 255代表明日方舟分区
    r = requests.post(url, data, headers=headers)
    addr = r.json()["data"]["rtmp"]["addr"]
    code = r.json()["data"]["rtmp"]["code"]
    if r.json()["data"]["status"] == "LIVE":
        await app.sendFriendMessage(member, MessageChain([Plain(addr)]))
        await app.sendFriendMessage(member, MessageChain([Plain(code)]))
        await app.send_group_message(group, MessageChain([Plain("直播间开启成功")]))
    else:
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间开启失败，原因：\n{r.json()['message']}")])
        )


async def end_gravity(app, group):
    url = "https://api.live.bilibili.com/room/v1/Room/stopLive"
    headers = {"cookie": gravity_cookie}
    data = {
        "room_id": "1925638",
        "csrf_token": gravity_bili_jct,
        "csrf": gravity_bili_jct,
        "platform": "pc",
    }
    r = requests.post(url, data, headers=headers)
    if r.json()["data"]["status"] == "PREPARING":
        await app.send_group_message(group, MessageChain([Plain("直播间关闭成功")]))


async def change_gravity(app, group, msg: str):
    text = msg.split(" ", 1)
    if len(text) < 2:
        return
    title = text[1]
    if len(title) > 20:
        await app.send_group_message(group, MessageChain([Plain("标题过长，请更改")]))
        return
    url = "https://api.live.bilibili.com/room/v1/Room/update"
    headers = {"cookie": gravity_cookie}
    data = {
        "room_id": "1925638",
        "csrf_token": gravity_bili_jct,
        "csrf": gravity_bili_jct,
        "title": title,
    }
    r = requests.post(url, data, headers=headers)
    print(r.json())
    if r.json()["msg"] == "ok":
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间标题已更改为：\n{title}")])
        )
    else:
        await app.send_group_message(
            group, MessageChain([Plain(f"直播间标题更改失败，原因：\n{r.json()['message']}")])
        )
