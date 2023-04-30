import asyncio
import datetime
import json
import os
import random
import re
import traceback
from typing import Union

import requests
# from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (HttpClientConfig,
                                             WebsocketClientConfig, config)
from graia.ariadne.entry import Friend, Group, Member
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import (FriendMessage, GroupMessage,
                                         TempMessage)
from graia.ariadne.event.mirai import (BotLeaveEventKick, BotMuteEvent,
                                       MemberMuteEvent, MemberUnmuteEvent)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (At, Forward, ForwardNode, Image,
                                           Plain, Quote, Voice)
from graia.ariadne.message.parser.base import (ContainKeyword, DetectPrefix,
                                               MatchContent, Mention,
                                               MentionMe)
from graia.broadcast import Broadcast
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graiax import silkcoder

from function.arknights import *
from function.bilibili import *
from function.canvas import *
from function.cherugo import *
from function.danmaku import *
from function.data import dancing_group
from function.excel import *
from function.image import *
from function.ini import *
from function.latex import *
from function.leetcode import *
from function.mute import *
from function.ouen import *
from function.pcr import *
from function.permission import *
from function.portune import *
from function.private import *
from function.repeat import *
from function.signup import *
from function.switch import *
from function.todotree import *
from function.weather import *

live = {}
sess = {}
bed = {}
rep = {}

app = Ariadne(
    connection=config(
        1424912867,  # 你的机器人的 qq 号
        "LLSShinoai",  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host="http://localhost:8098"),
        WebsocketClientConfig(host="http://localhost:8098"),
    ),
)

# app = Ariadne(MiraiSession(host="http://localhost:8098",
#                            verify_key="LLSShinoai", account=1424912867))
bcc = app.broadcast
inc = InterruptControl(bcc)


# saya = app.create(Saya)
# saya.install_behaviours(
#     app.create(BroadcastBehaviour),
# )
# with saya.module_context():
#     for module_info in pkgutil.iter_modules(["modules"]):
#         saya.require(f"modules.{module_info.name}")

mygroup = 958056260
hostqq = 349468958


def check_group():
    async def check_group_deco(app: Ariadne, group: Group):
        if int(read_from_ini('data/switch.ini', str(group.id), 'on', '0')) == 0:
            raise ExecutionStop
    return Depend(check_group_deco)


def nothost(*members: int):
    async def check_host(app: Ariadne, member: Union[Member, Friend]):
        if member.id in members:
            raise ExecutionStop
    return Depend(check_host)


def fromhost(*friends: int):
    async def check_ishost(app: Ariadne, friend: Union[Member, Friend]):
        if friend.id not in friends:
            raise ExecutionStop
    return Depend(check_ishost)


def check_permission(permission: int):
    async def check_permission_deco(app: Ariadne, group: Group, member: Member):
        if permission > permissionCheck(member.id, group.id):
            raise ExecutionStop
    return Depend(check_permission_deco)


@bcc.receiver(
    FriendMessage,
    decorators=[nothost(hostqq)],
)
async def forward_listener(app: Ariadne, message: MessageChain, friend: Friend):
    message_a = MessageChain([
        Plain('%s(%d)向您发送消息：\n' % (friend.nickname, friend.id))])
    message_a.extend(message.asSendable())
    await app.send_friend_message(hostqq, message_a)


@bcc.receiver(
    FriendMessage,
    decorators=[MatchContent("切噜")],
)
async def friend_message_handler(app: Ariadne, message: MessageChain, friend: Friend):
    await app.send_friend_message(friend, MessageChain([Plain('切噜~♪')]))


@bcc.receiver(TempMessage)
async def temp_message_handler(app: Ariadne, message: MessageChain, sender: Member):
    message_a = MessageChain([
        Plain('%s(%d)向您发送消息：\n' % (sender.name, sender.id))])
    message_a.extend(message.asSendable())
    await app.send_friend_message(hostqq, message_a)

ti = 0


@bcc.receiver(
    FriendMessage,
    decorators=[fromhost(hostqq)],
)
async def callme_listener(app: Ariadne, message: MessageChain, friend: Friend):
    # # TODO 移植cq中最高权限的私聊指令
    await priv_handler(app, message)


@bcc.receiver(
    GroupMessage,
    decorators=[nothost(hostqq), Mention(hostqq)],
)
async def callme_listener(app: Ariadne, message: MessageChain, group: Group, member: Member):
    # 监听事件永远最优先
    message_a = MessageChain([
        Plain("消息监听：\n%s(%d)在%s(%d)中可能提到了我：\n" % (member.name, member.id, group.name, group.id))])
    message_b = message.asSendable()
    message_a.extend(message_b)
    for i in range(0, len(message_a.__root__)):
        if message_a.__root__[i].type == 'At':
            message_a.__root__[i] = Plain(
                '@' + str(message_a.__root__[i].target))
    await app.send_group_message(mygroup, message_a)


@bcc.receiver(GroupMessage, decorators=[check_permission(3), DetectPrefix('switch ')])
async def switch_listener(app: Ariadne, message: MessageChain, group: Group, member: Member):
    # 开关指令不允许转义
    await switch(app, group, member, message.display)


@bcc.receiver(
    GroupMessage,
    decorators=[MatchContent("切噜"), check_group()],
)
async def cheru(app: Ariadne, group: Group, member: Member):
    await app.send_group_message(group, MessageChain([Plain('切噜~♪')]))

    # 此处发语音功能限定文件格式为silk，并且对框架具有一定版本要求，并且音质贼差
    filePath = './source/audio/cheru/'
    for i, j, k in os.walk(filePath):
        file = filePath + k[random.randint(0, len(k) - 1)]
    audio_bytes = await silkcoder.async_encode(file, ios_adaptive=True)
    await app.send_group_message(group, MessageChain([Voice(data_bytes=audio_bytes)]))


@bcc.receiver(
    GroupMessage,
    decorators=[ContainKeyword("recall"), check_permission(1)],
)
async def recall_listener(app: Ariadne, message: MessageChain):
    # bot撤回指令，不支持转义
    if message.has(Quote):
        for at in message.get(Quote):
            try:
                await app.recallMessage(at.id)
                await app.recallMessage(message.__root__[0].id)
            except:
                pass


# @bcc.receiver(
#     GroupMessage,
#     decorators=[MentionMe]
# )
# async def fun():

#     pass


@bcc.receiver(
    GroupMessage,
    decorators=[check_group()],
)
async def group_message_handler(app: Ariadne, message: MessageChain, group: Group, member: Member):
    # 若用户在黑名单当中则忽略消息
    if inban(member.id, group.id):
        return

    # 权限检查
    permissionflag = permissionCheck(member.id, group.id)

    try:
        # 复读
        # 这里我直接对Image类的源码直接进行了修改，重载==运算符使得图片可以进行复读，修改如下：
        # 增加了几行代码：

        '''

    class Image(InternalElement):

        ---

        def __eq__(self, other) -> bool:
            if other.__class__.__name__ == 'Image':
                return (self.imageId == other.imageId)
            else:
                return False

        ---

        '''

        if group.id not in rep:
            rep[group.id] = [message.__root__[1:], 1]
        else:
            message_a = message.__root__[1:]
            if rep[group.id][0] == message_a:
                rep[group.id][1] += 1
            else:
                rep[group.id] = [message_a, 1]
            if rep[group.id][1] == 3:
                await app.send_group_message(group, MessageChain(message_a))

        # bot 退群指令
        if member.id == hostqq and message.display == "\\withdraw":
            try:
                await app.revokeMessage(message.__root__[0].id)
                await app.kick(group, member)
            except:
                pass
            await app.quit(group)
            # TODO 将该群聊加入黑名单

        # help模块不支持转义
        if message.display == "help":
            sstr = "功能列表：" + \
                "\n目前可以公开使用的模块有：" +\
                "\n切噜语加密/解密：切噜语模块" +\
                "\npcr：pcr模块" +\
                "\npcrteam：pcr团队战模块" +\
                "\n天气：天气模块" +\
                "\n来点：图库模块" +\
                "\nmute：禁言模块" +\
                "\n订阅直播：b站直播间订阅模块" +\
                "\n不可以公开使用的模块有：" +\
                "\nbilibili：bilibili模块" +\
                "\ncanvas：canvas模块" +\
                "\ndanmaku：弹幕姬模块" +\
                "\nswitch：开关模块" +\
                "\ndefine：转义模块" +\
                "\ntimer：报时模块"
            await app.send_group_message(group, MessageChain([
                Plain(sstr)
            ]))
            return
        if message.display.startswith('help '):
            text = message.display.split(' ')
            if (len(text) != 2):
                return
            sstr = ''
            if text[1] == 'canvas':
                sstr = 'canvas模块：校内专用与canvas进行对接' +\
                    '\n目前具有的指令如下：' + \
                    '\ncanvas.todo：获取当前未完成的所有ddl' +\
                    '\ncanvas.todo.finish：获取当前所有ddl，包括已完成' +\
                    '\ncanvas.todo.add 日期 标题：在日期的时间上添加名为标题的ddl' +\
                    '\ncanvas.todo.del 标题：删除找到的第一个符合该标题的ddl'
            if text[1] == 'bilibili':
                sstr = 'bilibili模块：私人专用' +\
                    '\n目前具有的指令如下：' + \
                    '\nbilibili.signup：b站直播中心每日签到' +\
                    '\nbilibili.get：开启直播间并获得推流码，直播默认分区单机联机' +\
                    '\nbilibili.end：关闭直播间' +\
                    '\nbilibili.change 标题：更改直播间标题' +\
                    '\nbilibili.triple AV号/BV号：三连视频'
            if sstr != '':
                await app.send_group_message(group, MessageChain([
                    Plain(sstr)
                ]))

        # FIXME 用户向bot提供学号和密码用于登录canvas爬取数据
        if message.display.startswith("canvas.apply"):
            Localpath = './data/tongji.json'
            data = {}
            fr = open(Localpath, encoding='utf-8')
            data = json.load(fr)
            fr.close()

            for i in data["data"]:
                if i['qq'] == member.id:
                    m = MessageChain([At(member.id), Plain("您已在列表当中！")])
                    m.__root__[0].display = ''
                    await app.send_group_message(group, m)
                    break
            else:
                try:
                    await app.send_friend_message(member.id, MessageChain([
                        Plain("您即将向bot申请canvas爬取权限。这意味着：\n" +
                              "您需要将自己统一身份认证的学号以及密码私聊发送至bot\n" +
                              "我们可以保证您的学号和密码不会用于爬取canvas数据以外的地方\n" +
                              "如果您确定要申请此功能，请向bot私聊发送 /confirm 以继续运行\n")
                    ]))
                except:
                    m = MessageChain(
                        [At(member.id), Plain("您并不是bot好友！")])
                    m.__root__[0].display = ''
                    await app.send_group_message(group, m)

                global ti
                ti = 0

                @Waiter.create_using_function([FriendMessage], block_propagation=True)
                async def waiter(event: FriendMessage, waiter_member: Friend, waiter_message: MessageChain):
                    global ti
                    if ti != 0:
                        return event
                    if waiter_member.id == member.id:
                        if waiter_message.display != "/confirm":
                            await app.send_friend_message(member.id, MessageChain([
                                Plain("您取消了申请.")
                            ]))
                            return event
                        await app.send_friend_message(member.id, MessageChain([
                            Plain("请输入学号.")
                        ]))
                        ti += 1

                        @Waiter.create_using_function([FriendMessage], block_propagation=True)
                        async def waiter1(event1: FriendMessage, waiter1_member: Friend, waiter1_message: MessageChain):
                            global ti
                            if ti != 1:
                                return event
                            if waiter1_member.id == member.id:
                                await app.send_friend_message(member.id, MessageChain([
                                    Plain("请输入密码.")
                                ]))
                                ti += 1

                                @Waiter.create_using_function([FriendMessage], block_propagation=True)
                                async def waiter2(event2: FriendMessage, waiter2_member: Friend, waiter2_message: MessageChain):
                                    global ti
                                    if ti != 2:
                                        return event
                                    if waiter2_member.id == member.id:
                                        id = int(waiter1_message.display)
                                        password = waiter2_message.display
                                        try:
                                            add_person(
                                                waiter2_member.id, id, password)
                                            await app.send_friend_message(member.id, MessageChain([
                                                Plain("记录成功.")
                                            ]))
                                        except Exception as e:
                                            if str(e) == "验证码错误":
                                                await app.send_friend_message(member.id, MessageChain([
                                                    Plain("记录超时，请稍后再试.")
                                                ]))
                                            elif str(e) == "密码错误":
                                                await app.send_friend_message(member.id, MessageChain([
                                                    Plain("记录失败，请检查学号密码是否正确.")
                                                ]))
                                        return event
                                await inc.wait(waiter2)
                                return event
                        await inc.wait(waiter1)
                        return event
                await inc.wait(waiter)
                return

        # TODO thunder模块移植并投入使用

        # bilibili私人模块不支持转义
        if member.id == hostqq and message.display.startswith("bilibili"):
            await bilibili(app, group, message.display)

        if member.id == 1585165857 or member.id == 349468958:
            if message.display == "开始直播":
                await get_gravity(app, group, member)
            if message.display == "关闭直播":
                await end_gravity(app, group)
            if message.display.startswith("更改直播间标题"):
                await change_gravity(app, group, message.display)

        if member.id == hostqq and message.display == '生日测试':
            await readexcel(app, 958056260)

        msg = message.display  # 存储转义
        data = loadDefine()
        for i in data:
            if msg.find(i) == -1:
                continue
            # await app.send_group_message(group, MessageChain([Plain('发生转义：\n' + i + '->' + data[i])]))
            msg = msg.replace(i, data[i])
        msgs = message.as_persistent_string(exclude=[Forward])
        data = loadDefine()
        for i in data:
            if msgs.find(i) == -1:
                continue
            msgs = msgs.replace(i, data[i])

        # 权限增删
        if msg.startswith("set ") or msg.startswith("off "):
            await setMain(app, member, group, msgs)

        if (message.display == '?' or message.display == '？' or
                message.display == '草' or message.display == '艹'):
            flag = random.randint(0, 99)
            num = random.randint(5, 94)
            if (abs(flag - num) <= 5):
                await app.send_group_message(group, message.asSendable())

        # TODO 实装通过bigfun实现的会战信息查询系统
        if int(read_from_ini('data/switch.ini', str(group.id), 'pcrteam', '0')) == 1 and msg.startswith("pcrteam."):
            await pcrteam(app, group, msg)
        if (msg.startswith("pcr.")):
            await pcr(app, group, msg)
        '''
        if msg == '110':
            message = MessageChain([
                Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/99e465b59ddce9410aa8f5ae1a96a17da91736c4.png'),
                Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/90e102e603c4df5da446c7f9abad014b144f5836.png@150w_1o')
            ])
            await app.send_group_message(group, message)
        '''
        # TODO 实装TouHouRoll机

        # 直播订阅模块
        global live
        if msg.startswith("订阅直播 "):
            room_id = msg.replace("订阅直播 ", '')

            Localpath = './data/live.json'
            data = {}
            fr = open(Localpath, encoding='utf-8')
            data = json.load(fr)
            fr.close()

            for i in data['data']:
                if room_id == str(i['room_id']):
                    if group.id in i['group']:
                        await app.send_group_message(group, MessageChain([Plain("这个直播已经在被视奸啦！")]))
                        break
            else:
                try:
                    if room_id not in live:
                        live[room_id] = asyncio.create_task(
                            entrence(app, room_id))
                    info = get_info(room_id)
                    await app.send_group_message(group, MessageChain([Plain("开启对%s(%d)的直播间订阅" % (info['uname'], info['uid']))]))
                    livewrite(group.id, int(room_id))
                except:
                    await app.send_group_message(group, MessageChain([Plain("开启直播视奸失败，请检查房间号")]))
                    del live[room_id]

        if msg.startswith('取消订阅 '):
            room_id = msg.replace("取消订阅 ", '')

            Localpath = './data/live.json'
            data = {}
            fr = open(Localpath, encoding='utf-8')
            data = json.load(fr)
            fr.close()

            for i in data['data']:
                if room_id == str(i['room_id']):
                    if group.id in i['group']:
                        if (len(i['group']) > 1):
                            i['group'].remove(group.id)
                        else:
                            data['data'].remove(i)
                            live[room_id].cancel()
                            del live[room_id]
                        with open(Localpath, "w") as fw:
                            jsObj = json.dumps(data)
                            fw.write(jsObj)
                            fw.close()
                        pass
                        info = get_info(room_id)
                        await app.send_group_message(group, MessageChain([Plain("关闭对%s(%d)的直播间订阅" % (info['uname'], info['uid']))]))
                        break

        if msg.startswith('查询直播间 '):
            room_id = msg.replace("查询直播间 ", '')
            info = get_info(room_id)
            if not 'msg' in info:
                sstr = f'用户名：{info["uname"]}({info["uid"]})\n直播间标题：{info["title"]}\n' + \
                    f'直播分区：{info["parent_area_name"]} - {info["area_name"]}\n' + \
                    f'直播间地址：https://live.bilibili.com/{info["room_id"]}\n' + \
                    f'直播间状态：{"直播中" if info["live_status"] else "未开播"}\n直播关键帧：'
                await app.send_group_message(group, MessageChain([
                    Plain(sstr),
                    Image(url=info['keyframe'])
                ]))
            else:
                await app.send_group_message(group, MessageChain([
                    Plain(info['msg'])
                ]))
            pass
        # canvas任务爬取模块
        global sess
        if msg.startswith('canvas.'):
            try:
                if member.id not in sess:
                    temp = ids_login(member.id)
                    sess[member.id] = temp
                await canvas(app, group, member, msg, sess[member.id])
            except Exception as e:
                if str(e) == "账号未记录":
                    await app.send_group_message(group, MessageChain([Plain(
                        '并没有记录任何学号信息，如需使用此功能请在群内发送 canvas.apply 以向bot申请。\n' +
                        '注意：在此之前请检查您是否与bot互为好友'
                    )]))
                elif str(e) == "验证码错误":
                    await app.send_group_message(group, MessageChain([Plain(
                        '登录超时，请稍后再试。'
                    )]))
                else:
                    print(e)
                    print(str(e))
                    print(e.args)
                    print(repr(e))

        if msg.startswith('courses.'):
            try:
                if member.id not in sess:
                    temp = ids_login(member.id)
                    sess[member.id] = temp
                await courses(app, group, member, msg, sess[member.id])
            except Exception as e:
                if str(e) == "账号未记录":
                    await app.send_group_message(group, MessageChain([Plain(
                        '并没有记录任何学号信息，如需使用此功能请在群内发送 canvas.apply 以向bot申请。\n' +
                        '注意：在此之前请检查您是否与bot互为好友'
                    )]))
                elif str(e) == "验证码错误":
                    await app.send_group_message(group, MessageChain([Plain(
                        '登录超时，请稍后再试。'
                    )]))
                else:
                    print(e)
                    print(str(e))
                    print(e.args)
                    print(repr(e))

        # 天气模块
        if msg.split(' ')[0].endswith('天气'):
            await weather(app, inc, group, member, msg)

        # if member.id == hostqq and msg == ("测试拉取"):
        #     print('正在进行消息拉取...')
        #     mmsg = private_msg(app)
        #     if mmsg:
        #         await app.send_group_message(group, mmsg)
        #     else:
        #         print('并没有拉取到东西')

        # TODO 4m3和1块钱公告爬取

        if member.id == hostqq and msg.startswith("danmaku.end"):
            t = live.get((group.id, member.id), None)
            if t:
                t.cancel()
                await app.send_group_message(group, MessageChain([Plain("直播视奸停止")]))
            else:
                m = MessageChain([At(hostqq), Plain("你并没有在视奸")])
                m.__root__[0].display = ''
                await app.send_group_message(group, m)

        if member.id == hostqq and msg == "packup":
            try:
                await packup(app, group.id)
                await app.send_group_message(group, MessageChain([Plain("备份群成员信息成功")]))
            except:
                await app.send_group_message(group, MessageChain([Plain("备份群成员信息失败")]))
                traceback.print_exc()
                await app.send_group_message(group, MessageChain([Plain(traceback.format_exc())]))

        if member.id == hostqq and msg == "packupall":
            try:
                list = await app.get_group_list()
                for i in list:
                    await packup(app, i.id)
                await app.send_group_message(group, MessageChain([Plain("备份所有群成员信息成功")]))
            except:
                await app.send_group_message(group, MessageChain([Plain("备份所有群成员信息失败")]))
                traceback.print_exc()
                await app.send_group_message(group, MessageChain([Plain(traceback.format_exc())]))

        # FIXME leetcode每日题库好像有点问题记得修
        if msg == "leetcode.daily":
            await get_daily(app, group)
        if msg == "leetcode.rand":
            await get_rand(app, group)
        if msg == "luogu.rand":
            await luogu_rand(app, group)
        if msg == "签到":
            await app.send_group_message(group, MessageChain([Plain(signup(member.id))]))
        # print(await app.getMember(group, 1424912867))
        if permissionflag >= 1 and msg.startswith("mute"):
            mute_member(app, group, message)

        if msg.startswith("latex "):
            await latex(app, group, msg)

        if message.display.startswith("define "):
            if (permissionCheck(member.id, group.id) == 3):
                define(message.display)

        # 切噜语模块
        if msg.startswith("切噜语加密 "):
            s = msg.replace("切噜语加密 ", '', 1)
            if len(s) > 500:
                msg = '切、切噜太长切不动勒切噜噜...'
            else:
                msg = '切噜~♪' + str2cheru(s)
            await app.send_group_message(group, MessageChain([Plain(msg)]))
        elif msg.startswith("切噜语解密"):
            s = msg.replace("切噜语解密 切噜~♪", '', 1)
            if s == '':
                return
            msg = cheru2str(s)
            m = MessageChain([At(member.id), Plain(msg)])
            m.__root__[0].display = ''
            await app.send_group_message(group, m)

        # 图库模块
        if msg.startswith("来点"):
            # FIXME 啊啊啊啊啊啊我TM一不小心把图库给删了啊啊啊啊啊啊
            await seImage(app, group, msg)

        if msg.startswith("举牌 "):
            text = msg.split(' ')
            if len(text) >= 2:
                txt = text[1]
                for i in text[2:]:
                    txt += ' ' + i
            await ouen(app, txt, group)

        # 选择模块
        if msg.startswith("choice "):
            s = msgs
            while s.find('  ') != -1:
                s = s.replace('  ', ' ')
            s = s.replace("choice ", '', 1)
            s_msg = choice(s)
            await app.send_group_message(group, MessageChain.from_persistent_string(s_msg))
        if msg.startswith("选择 "):
            s = msgs
            if random.randrange(0, 100) == random.randrange(0, 100):
                await app.send_group_message(group, MessageChain([Plain("不选")]))
            else:
                while s.find('  ') != -1:
                    s = s.replace('  ', ' ')
                s = s.replace("选择 ", '', 1)
                s_msg = choice(s)
                await app.send_group_message(group, MessageChain.from_persistent_string(s_msg))
        if msg.startswith("选择"):  # 多次选择
            s = msgs
            while s.find('  ') != -1:
                s = s.replace('  ', ' ')
            pattern = re.compile(r'选择\d+')
            p = pattern.findall(s)
            if p:
                nn = int(p[0].replace('选择', ''))
                if nn > 1000000:
                    await app.send_group_message(group, MessageChain([Plain("选择次数太多选不了噜~")]))
                else:
                    op = s.split(' ')[1:]
                    if not op:
                        await app.send_group_message(group, MessageChain([Plain("选啥")]))
                        return
                    while op[-1] == '':
                        del op[-1]
                    if not op:
                        await app.send_group_message(group, MessageChain([Plain("选啥")]))
                    else:
                        ans = [0] * len(op)
                        for i in range(nn):
                            while (True):
                                a = random.randint(-1, len(op))
                                if a != -1 and a != len(op):
                                    ans[a] += 1
                                    break
                        sstr = '{}*{}'.format(op[0], ans[0])
                        for i in range(1, len(op)):
                            sstr += ', {}*{}'.format(op[i], ans[i])
                        await app.send_group_message(group, MessageChain.from_persistent_string(sstr))

        # echo模块
        if msg.startswith("echo ") and msg != "echo ":
            message_a = message
            message_a.__root__[1].text = message_a.__root__[
                1].text.replace('echo ', '', 1)
            await app.send_group_message(group, message_a.asSendable())
            pass

        if message.display.find("后提醒我") != -1:
            await remindme(app, group.id, member.id, message.copy())

        mmm = message.as_persistent_string(exclude=[Forward])
        if mmm.find('[mirai:At:{"target":%d' % app.account) != -1:
            text = mmm.split(' ')
            if len(text) == 2:
                if text[1] == '起床':
                    t = datetime.datetime.now() - datetime.timedelta(hours=4)
                    if group.id not in bed:
                        bed[group.id] = {}
                    if member.id not in bed[group.id] or bed[group.id][member.id][0].date() != t.date():
                        bed[group.id][member.id] = [t, 'on']
                    else:
                        ss = '你今天已经起床过了哟！'
                        await app.send_group_message(group, MessageChain([Plain(ss)]))
                        return

                    if 'live_number' not in bed[group.id]:
                        bed[group.id]['live_number'] = 1
                    else:
                        bed[group.id]['live_number'] += 1
                    if 'day' not in bed:
                        bed['day'] = t.date()
                    else:
                        tb = bed['day']
                        if t.date() != tb:
                            bed[group.id]['live_number'] = 1
                        bed['day'] = t.date()
                    ss = '你是今天第%d个起床的群友哦！' % bed[group.id]['live_number']
                    await app.send_group_message(group, MessageChain([Plain(ss)]))
                    return
                elif text[1] == '睡觉':
                    t = datetime.datetime.now() - datetime.timedelta(hours=4)
                    if group.id not in bed:
                        ss = '你今天还没有起过床哟！'
                    elif member.id not in bed[group.id]:
                        ss = '你今天还没有起过床哟！'
                    elif bed[group.id][member.id][0].date() != t.date():
                        ss = '你今天还没有起过床哟！'
                    elif bed[group.id][member.id][1] == 'off':
                        ss = '你已经睡觉了哟！'
                    else:
                        td = t - bed[group.id][member.id][0]
                        ss = '你今天清醒了%s哟！' % time_to_str(
                            int(td.total_seconds()))
                        bed[group.id][member.id] = [t, 'off']
                        await app.send_group_message(group, MessageChain([Plain(ss)]))
                        return
                    await app.send_group_message(group, MessageChain([Plain(ss)]))
                    return

        # 测试拉取

        if message.display.startswith("测试拉取"):
            sstr = message.display.split(' ', 2)
            if len(sstr) < 2:
                await app.send_group_message(group, MessageChain([Plain("缺少参数")]))
            else:
                Localpath = './data/cookies.json'
                with open(Localpath, 'r', encoding='utf8')as fp:
                    cookies = json.load(fp)
                data = cookies[sstr[1]]
                print('正在进行消息拉取...')
                msg_list = private_msg(app, data)
                if msg_list:
                    await app.send_group_message(group, msg_list)
                else:
                    await app.send_group_message(group, MessageChain([Plain("没有拉取到东西")]))
        # pcr运势模块
        if message.display == "运势":
            t = datetime.datetime.now() - datetime.timedelta(hours=0)
            # 此处p是指运势
            if not 'p' in bed:
                # print("开机到现在第一个抽运势")
                bed['p'] = {}
            if not member.id in bed['p']:
                # print(f"{member.name}第一次抽运势")
                bed['p'][member.id] = [t, '', {}]
            # print(bed['p'][member.id])
            await portune(app, group, member.id, bed['p'][member.id])

        # 今日老婆模块
        if message.display == "今日老婆":
            # 在bed中建立wife存储今日老婆
            if not 'wife' in bed:
                bed['wife'] = {}
            now = datetime.datetime.today()
            add = datetime.timedelta(hours=0)
            now -= add
            # 如果换日，则清空
            if not now.date() in bed['wife']:
                bed['wife'] = {}
                bed['wife'][now.date()] = {}
            if not group.id in bed['wife'][now.date()]:
                bed['wife'][now.date()][group.id] = {}
            n1 = member
            if not member.id in bed['wife'][now.date()][group.id]:
                ms = await app.get_member_list(group)
                if len(ms) - len(bed['wife'][now.date()][group.id]) != 1:
                    while (n1.id == member.id or n1.id in bed['wife'][now.date()][group.id]):
                        n1 = random.choice(ms)
                    bed['wife'][now.date()][group.id][n1.id] = member.id
                    bed['wife'][now.date()][group.id][member.id] = n1.id
                else:
                    n1 = await app.get_friend(app.account)
                    await app.send_group_message(group.id, MessageChain([
                        At(member), Plain(
                            " 群里没人能当你老婆了，那切噜就勉为其难的当你一天老婆吧！\n你今天的老婆是：\n"),
                        Img(data_bytes=await n1.get_avatar(140)),
                        Plain(f"\n{n1.nickname}（{n1.id}）")
                    ]))
                    return
            else:
                n1 = bed['wife'][now.date()][group.id][member.id]
                n1 = await app.get_member(group, n1)
            await app.send_group_message(group, MessageChain([
                At(member), Plain(" 你今天的老婆是：\n"),
                Img(data_bytes=await n1.get_avatar(140)),
                Plain(f"\n{n1.name}（{n1.id}）")
            ]))

        # 群老婆和群sabi
        if msg == "群老婆":
            # 在bed中建立allwife存储大家的老婆
            if not 'allwife' in bed:
                bed['allwife'] = {}
            now = datetime.datetime.today()
            add = datetime.timedelta(hours=0)
            now -= add
            # 如果换日，则清空
            if not now.date() in bed['allwife']:
                bed['allwife'] = {}
                bed['allwife'][now.date()] = {}
            n1 = member
            if not group.id in bed['allwife'][now.date()]:
                n1 = random.choice(await app.get_member_list(group))
                bed['allwife'][now.date()][group.id] = n1.id
            else:
                n1 = await app.get_member(group, bed['allwife'][now.date()][group.id])
            await app.send_group_message(group, MessageChain([
                Plain("今天你群的老婆是：\n"),
                Img(data_bytes=await n1.get_avatar(140)),
                Plain(f"\n{n1.name}（{n1.id}）")
            ]))

        # if msg == "群sabi":
        #     # 在bed中建立sabi存储
        #     if not 'sabi' in bed:
        #         bed['sabi'] = {}
        #     now = datetime.datetime.today()
        #     add = datetime.timedelta(hours=0)
        #     now -= add
        #     # 如果换日，则清空
        #     if not now.date() in bed['sabi']:
        #         bed['sabi'] = {}
        #         bed['sabi'][now.date()] = {}
        #     n1 = member
        #     if not group.id in bed['sabi'][now.date()]:
        #         n1 = random.choice(await app.get_member_list(group))
        #         bed['sabi'][now.date()][group.id] = n1.id
        #     else:
        #         n1 = await app.get_member(group, bed['sabi'][now.date()][group.id])
        #     await app.send_group_message(group, MessageChain([
        #         Plain("今天你群的sabi是：\n"),
        #         Img(data_bytes=await n1.get_avatar(140)),
        #         Plain(f"\n{n1.name}（{n1.id}）")
        #     ]))

        # 明日方舟模块
        if msg.startswith('搜索作战 '):
            text = msg.split(' ')
            flag = False
            print(text)
            if len(text) > 2:
                if "是" == text[2] or text[2] == "全部":
                    flag = True
            await app.send_group_message(group, MessageChain([Plain(search_stages(text[1], flag))]))

        if msg.startswith('搜索素材 '):
            text = msg.split(' ')
            start = 0
            end = 5
            if len(text) == 3:
                end = int(text[2])
            if len(text) == 4:
                start = int(text[2])
                end = int(text[3])
            if start > end:
                start, end = end, start
            await app.send_group_message(group, MessageChain([Plain(search_items(text[1], end, start))]))
        if msg.startswith('添加缩写 '):
            await app.send_group_message(group, MessageChain([Plain(arksetDefine(msg))]))
        if msg.startswith('删除缩写 '):
            await app.send_group_message(group, MessageChain([Plain(arkoffDefine(msg))]))
        if msg.startswith('查询缩写 '):
            await app.send_group_message(group, MessageChain([Plain(arkexpand(msg))]))
        if msg.startswith('搜索公招'):
            if len(message.__root__) < 3 or message.__root__[2].type != "Image":
                return
            url = message.__root__[2].url
            ans, d = arkRecruit(url)
            fwd_nodeList = []
            mmm = f"识别到{len(ans)}个tag：\n"
            for i in ans:
                mmm += f'{i} '
            mmm = mmm[:-1]
            fwd_nodeList = [
                ForwardNode(
                    target=member,
                    time=datetime.datetime.now(),
                    message=MessageChain(mmm),
                )
            ]
            m = 1
            for i in d:
                sstr = ''
                for j in i[0]:
                    sstr += j + '，'
                sstr = sstr[:-1] + '：'
                sstr += '\n'
                n = 6
                for j in i[1]:
                    sstr += j['n'] + '，'
                    n = min(n, j['r'])
                sstr = sstr[:-1]
                m = max(m, n)
                fwd_nodeList.append(
                    ForwardNode(
                        target=member,
                        time=datetime.datetime.now(),
                        message=MessageChain(sstr),
                    )
                )
            fwd_nodeList[0].message_chain.extend(f"\n保底{m}星干员")
            message = MessageChain(Forward(nodeList=fwd_nodeList))
            await app.send_group_message(group, message)

        # if msg.startswith('ttest '):
        #     url = message.__root__[2].url
        #     await app.send_group_message(group, MessageChain([Plain(url)]))
            # arkRecruit(url)

        if msg == 'help.todo':
            await app.send_group_message(group, MessageChain([Plain(help_todo)]))
        if msg.startswith('todo.'):
            m = funTodo(msg, member.id)
            if m:
                await app.send_group_message(group, MessageChain([Plain(m)]))

        # 瞎搞模块
        if message.display == "咕一下":
            await app.send_group_message(group, MessageChain([Plain(dove())]))
        if msg.find("/生日快乐") != -1 and len(msg.replace("/生日快乐", "")) == 0:
            await app.send_group_message(group, MessageChain([Plain('禁止/生日快乐')]))
        if message.has(At):
            if message.display.find('recall') != -1:
                return
            flag = 0
            for at in message.get(At):
                if at.target == 1424912867:
                    at.target = member.id
                    flag = 1
            if flag == 0:
                return
            if message.display.find("/生日快乐") != -1:
                try:
                    await set_mute(app, group, [member.id], 600)
                except:
                    pass
            await app.send_group_message(group, message.asSendable())

        pattern = re.compile(r'异.*世.*相.*遇.*尽.*享.*美.*味.*')
        if pattern.search(message.display) != None:
            await app.send_group_message(group, MessageChain([Plain("来一份二刺猿桶")]))

    except KeyboardInterrupt:
        print("quit")
    except Exception as e:
        traceback.print_exc()
        await app.send_group_message(group, MessageChain([Plain(traceback.format_exc())]))


@bcc.receiver(
    GroupMessage,
    decorators=[check_group(), DetectPrefix("expand ")]
)
async def expand_listener(app: Ariadne, message: MessageChain, group: Group):
    # 瞎搞模块
    try:
        text = message.display.split(' ')
        if len(text) >= 2:
            txt = text[1]
            for i in text[2:]:
                txt += ' ' + i
        # FIXME 当txt全为空格组成时会报错
        if not txt.isascii():
            await app.send_group_message(group, MessageChain([Plain("你好好反思反思你在说什么")]))
            return
        url = "https://lab.magiconch.com/api/nbnhhsh/guess"
        r = requests.post(url, data={"text": txt}).json()
        if r:
            r = r[0]
            if 'inputting' in r and r['inputting']:
                ss = "%s 有可能是：" % r['name']
                r['inputting'].sort()
                for i in r['inputting']:
                    ss += '\n' + i
            elif 'trans' in r and r['trans']:
                ss = "%s 可能是：" % r['name']
                r['trans'].sort()
                for i in r['trans']:
                    ss += '\n' + i
            else:
                ss = "你在说些什么"
        else:
            ss = "我听不懂"
        await app.send_group_message(group, MessageChain([Plain(ss)]))
    except Exception as e:
        traceback.print_exc()
        await app.send_group_message(group, MessageChain([Plain(traceback.format_exc())]))


@bcc.receiver(MemberMuteEvent)
async def member_mute_handler(app: Ariadne, event: MemberMuteEvent):
    if (int(read_from_ini('data/switch.ini', str(event.member.group.id), 'on', '0')) == 0):
        return

    if event.operator == None:
        return
    sstr = time_to_str(event.durationSeconds)
    # print(sstr)
    message = MessageChain([
        Plain('%s(%d)被%s(%d)禁言%s' % (event.member.name, event.member.id, event.operator.name, event.operator.id, sstr))])
    await app.send_group_message(event.member.group.id, message)
    # print(MemberMuteEvent.durationSeconds)


@bcc.receiver(MemberUnmuteEvent)
async def member_mute_handler(app: Ariadne, event: MemberUnmuteEvent):
    if (int(read_from_ini('data/switch.ini', str(event.member.group.id), 'on', '0')) == 0):
        return

    if event.operator == None:
        return
    message = MessageChain([
        Plain('%s(%d)被%s(%d)解除禁言' % (event.member.name, event.member.id, event.operator.name, event.operator.id))])
    await app.send_group_message(event.member.group.id, message)
    # app.getMember()


@bcc.receiver(BotMuteEvent)
async def bot_mute_handler(app: Ariadne, event: BotMuteEvent):
    if event.operator.id == hostqq:
        return
    if event.durationSeconds <= 3600:
        return
    # TODO 黑名单系统
    await app.send_group_message(mygroup, MessageChain([Plain(
        '在%s(%d)被%s(%d)禁言%s，已自动从群聊中退出并将所在群和禁言人列入黑名单' %
        (event.operator.group.name, event.operator.group.id,
         event.operator.name, event.operator.id,
         time_to_str(event.durationSeconds))
    )]))
    await app.quit(event.operator.group)


@bcc.receiver(BotLeaveEventKick)
async def bot_kicked_hanler(app: Ariadne, event: BotLeaveEventKick):
    # TODO 黑名单系统
    await app.send_group_message(mygroup, MessageChain([Plain(
        '在%s(%d)被%s(%d)移出群聊，已将群和操作人列入黑名单' %
        (event.operator.group.name, event.operator.group.id,
         event.operator.name, event.operator.id)
    )]))


@bcc.receiver(ApplicationLaunched)
async def repeattt(app: Ariadne):

    Localpath = './data/cookies.json'
    with open(Localpath, 'r', encoding='utf8')as fp:
        cookies = json.load(fp)
    settings = cookies['settings']
    for i in settings:
        if settings[i] == 1:
            asyncio.create_task(private_msg_init(app, cookies[i]))

    # TODO 实装整点报时之类的功能
    asyncio.create_task(clock(app))

    global live
    Localpath = './data/live.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    for i in data["data"]:
        live[str(i['room_id'])] = asyncio.create_task(
            entrence(app, str(i['room_id'])))

app.launch_blocking()
