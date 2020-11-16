import asyncio
import datetime
import operator
import random
from asyncio.tasks import Task, create_task
from re import escape
from typing import Dict, Optional

from graia.application import GraiaMiraiApplication, Session
from graia.application.entry import (BotMuteEvent, FriendMessage, GroupMessage,
                                     MemberMuteEvent, MemberUnmuteEvent)
from graia.application.event.lifecycle import ApplicationLaunched
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Image, Plain
from graia.broadcast import Broadcast

from function.bilibili import bilibili, pcr, pcrteam
from function.canvas import canvas
from function.cherugo import cheru2str, str2cheru
from function.danmaku import danmaku, startup
from function.image import seImage
from function.ini import read_from_ini, write_in_ini
from function.mute import mute_member, time_to_str
from function.permission import permissionCheck, setMain
from function.repeat import clock, repeat
from function.signup import (atme, choice, define, loadDefine, paraphrase,
                             signup)
from function.switch import switch

a = {}

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8098",  # 填入 httpapi 服务运行的地址
        authKey="LLSShinoai",  # 填入 authKey
        account=1424912867,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

mygroup = 958056260


@bcc.receiver(FriendMessage)
async def friend_message_handler(app: GraiaMiraiApplication, message: MessageChain, friend: Friend):
    if (friend.id != 349468958):
        message_a = MessageChain(__root__=[
            Plain(friend.nickname + '(' + str(friend.id) + ')' + "向您发送消息：\n")])
        message_b = message.asSendable()
        message_a.plus(message_b)
        await app.sendFriendMessage(349468958, message_a)


@bcc.receiver(GroupMessage)
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    '''
    if message.asDisplay() == '发送' and member.id == 349468958:
        aaa = [1138925965, 980644912, 1002841584, 1002962655, 596215633, 1125282555]
        sss = '今天是切噜妈妈的生日！把这条消息发送到5个群可以凭截图找切噜妈妈获得100元生日红包！我试过了是真的，妈妈真的给我发红包了！今天真的是切噜妈妈的生日！'
        ss = '1234567890-'
        for i in aaa:
            await app.sendGroupMessage(i, MessageChain.create([Plain(sss)]))
    '''

    if (member.id != 349468958):
        msg = message.asSerializationString()
        if(atme(msg)):
            message_a = MessageChain(__root__=[
                Plain("消息监听：\n" + member.name + '(' + str(member.id) + ")在" + group.name + '(' + str(group.id) + ")中可能提到了我：\n")])
            message_b = message.asSendable()
            message_a.plus(message_b)
            await app.sendGroupMessage(mygroup, message_a)

    msg = message.asDisplay()
    data = loadDefine()
    for i in data:
        if msg.find(i) == -1:
            continue
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain('发生转义：\n' + i + '->' + data[i])]))
        msg = msg.replace(i, data[i])
    msgs = message.asSerializationString()
    data = loadDefine()
    for i in data:
        if msgs.find(i) == -1:
            continue
        msgs = msgs.replace(i, data[i])

    if member.id == 349468958 and msg.startswith("bilibili"):
        asyncio.create_task(bilibili(app, group, msg))

    if msg.startswith("switch "):
        asyncio.create_task(switch(app, group, member, msg))

    if msg.startswith("set ") or msg.startswith("off "):
        asyncio.create_task(setMain(app, member, group, msgs))

    if (int(read_from_ini('data/switch.ini', str(group.id), 'on', '0')) == 0):
        return

    if (message.asDisplay() == '?' or message.asDisplay() == '？' or
        message.asDisplay() == '草' or message.asDisplay() == '艹' or
            message.asDisplay() == '[图片]'):
        flag = random.randint(0, 99)
        num = random.randint(5, 94)
        if(abs(flag - num) <= 5):
            await app.sendGroupMessage(group, message.asSendable())

    # TODO 实装通过bigfun实现的会战信息查询系统
    if int(read_from_ini('data/switch.ini', str(group.id), 'pcrteam', '0')) == 1 and msg.startswith("pcrteam."):
        asyncio.create_task(pcrteam(app, group, msg))
    if (msg.startswith("pcr.")):
        asyncio.create_task(pcr(app, group, msg))
    '''
    if msg == '110':
        message = MessageChain.create([
            Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/99e465b59ddce9410aa8f5ae1a96a17da91736c4.png'),
            Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/90e102e603c4df5da446c7f9abad014b144f5836.png@150w_1o')
        ])
        await app.sendGroupMessage(group, message)
    '''
    # TODO 实装TouHouRoll机

    # FIXME 直播间开播提示而不是弹幕姬
    if member.id == 349468958 and msg.startswith("danmaku "):
        roomid = msg.replace("danmaku ", '')
        global a
        if (group.id, member.id) in a:
            await app.sendGroupMessage(group, MessageChain.create([Plain("你在群里已经有一个正在视奸的直播啦")]))
        else:
            a[group.id, member.id] = asyncio.create_task(
                startup(app, group, roomid))
            await app.sendGroupMessage(group, MessageChain.create([Plain("直播视奸开始")]))

    # TODO canvas任务爬取
    if msg.startswith('canvas'):
        asyncio.create_task(canvas(app, group, member, msg))

    if member.id == 349468958 and msg.startswith("danmaku.end"):
        t = a.get((group.id, member.id), None)
        if t:
            t.cancel()
            await app.sendGroupMessage(group, MessageChain.create([Plain("直播视奸停止")]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([At(349468958), Plain("你并没有在视奸")]))

    if msg == "签到":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(signup(member.id))]))
    # print(await app.getMember(group, 1424912867))
    if member.id == 349468958 and msg.startswith("mute"):
        mute_member(app, group, message)

    if message.asDisplay().startswith("define "):
        if(permissionCheck(member.id, group.id) == 3):
            define(message.asDisplay())

    if msg == "切噜":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain('切噜~♪')]))
    if msg.startswith("切噜 "):
        s = msg.replace("切噜 ", '', 1)
        if len(s) > 500:
            msg = '切、切噜太长切不动勒切噜噜...'
        else:
            msg = '切噜~♪' + str2cheru(s)
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(msg)]))
    elif msg.startswith("切噜~♪"):
        s = msg.replace("切噜~♪", '', 1)
        if s == '':
            return
        msg = cheru2str(s)
        await app.sendGroupMessage(group, MessageChain(__root__=[At(member.id), Plain(msg)]))

    if msg.startswith("来点"):
        asyncio.create_task(seImage(app, group, msg))
    if msg.startswith("choice "):
        ss = msgs.split(']', 1)
        s = ss[1]
        while s.find('  ') != -1:
            s = s.replace('  ', ' ')
        s = s.replace("choice ", '', 1)
        msg = choice(s)
        await app.sendGroupMessage(group, MessageChain.fromSerializationString(msg))
    if msg.startswith("选择 "):
        print(message.__root__)
        ss = msgs.split(']', 1)
        s = ss[1]
        while s.find('  ') != -1:
            s = s.replace('  ', ' ')
        s = s.replace("选择 ", '', 1)
        msg = choice(s)
        await app.sendGroupMessage(group, MessageChain.fromSerializationString(msg))
    if msg == "/生日快乐":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain('禁止/生日快乐')]))
    if msg.startswith("echo ") and msg != "echo ":
        message_a = message
        message_a.__root__[1].text = message_a.__root__[
            1].text.replace('echo ', '', 1)
        await app.sendGroupMessage(group, message_a.asSendable())
        pass
    if message.has(At):
        flag = 0
        for at in message.get(At):
            if at.target == 1424912867:
                at.target = member.id
                flag = 1
        if flag == 0:
            return
        await app.sendGroupMessage(group, message.asSendable())


@bcc.receiver(MemberMuteEvent)
async def member_mute_handler(app: GraiaMiraiApplication, event: MemberMuteEvent):
    if event.operator == None:
        return
    sstr = time_to_str(event.durationSeconds)
    # print(sstr)
    message = MessageChain(__root__=[
        Plain(event.member.name + '(' + str(event.member.id) + ')被' + event.operator.name + '(' + str(event.operator.id) + ')禁言' + sstr)])
    await app.sendGroupMessage(event.member.group.id, message)
    # print(MemberMuteEvent.durationSeconds)


@bcc.receiver(MemberUnmuteEvent)
async def member_mute_handler(app: GraiaMiraiApplication, event: MemberUnmuteEvent):
    if event.operator == None:
        return
    message = MessageChain(__root__=[
        Plain(event.member.name + '(' + str(event.member.id) + ')被' + event.operator.name + '(' + str(event.operator.id) + ')解除禁言')])
    await app.sendGroupMessage(event.member.group.id, message)
    # app.getMember()


@bcc.receiver(BotMuteEvent)
async def bot_mute_handler(app: GraiaMiraiApplication, event: BotMuteEvent):
    if event.operator.id == 349468958:
        return
    if event.durationSeconds < 43200:
        return
    await app.quit(event.operator.group)
    # TODO 黑名单系统
    await app.sendGroupMessage(mygroup, MessageChain.create([Plain(
        "在" + event.operator.group.name + '(' + str(event.operator.group.id) + ')被' +
        event.operator.name + '(' + str(event.operator.id) + ')禁言' + time_to_str(event.durationSeconds) +
        '，已自动从群聊中退出并将所在群和禁言人列入黑名单')]))
    pass


@bcc.receiver(ApplicationLaunched)
async def repeattt(app: GraiaMiraiApplication):
    # TODO 实装整点报时之类的功能
    asyncio.create_task(clock(app))
    pass

app.launch_blocking()
