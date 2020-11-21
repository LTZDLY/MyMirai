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
from graia.application.event.messages import TempMessage
from graia.application.event.mirai import BotLeaveEventKick
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Image, Plain, Quote
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter

from function.bilibili import bilibili
from function.canvas import canvas, createlink
from function.cherugo import cheru2str, str2cheru
from function.danmaku import danmaku, startup
from function.image import seImage
from function.ini import read_from_ini, write_in_ini
from function.mute import mute_member, time_to_str
from function.pcr import pcr, pcrteam
from function.permission import permissionCheck, setMain
from function.repeat import clock, repeat
from function.signup import (atme, choice, define, loadDefine, paraphrase,
                             signup)
from function.switch import switch
from function.weather import weather

a = {}
sess = {}

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
inc = InterruptControl(bcc)

mygroup = 958056260


@bcc.receiver(FriendMessage)
async def friend_message_handler(app: GraiaMiraiApplication, message: MessageChain, friend: Friend):
    if (friend.id != 349468958):
        message_a = MessageChain.create([
            Plain(friend.nickname + '(' + str(friend.id) + ')' + "向您发送消息：\n")])
        message_b = message.asSendable()
        message_a.plus(message_b)
        await app.sendFriendMessage(349468958, message_a)


@bcc.receiver(TempMessage)
async def temp_message_handler(app: GraiaMiraiApplication, message: MessageChain, sender: Member):
    message_a = MessageChain.create([
        Plain(sender.nickname + '(' + str(sender.id) + ')' + "向您发送消息：\n")])
    message_b = message.asSendable()
    message_a.plus(message_b)
    await app.sendFriendMessage(349468958, message_a)


@bcc.receiver(GroupMessage)
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):

    # FIXME 用户向bot提供学号和密码用于登录canvas爬取数据
    '''
    if message.asDisplay().startswith("canvas.apply"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain("发送 /confirm 以继续运行")
        ]))
        id = ''
        password = ''

        @Waiter.create_using_function([GroupMessage])
        def waiter(
            event: GroupMessage, waiter_group: Group,
            waiter_member: Member, waiter_message: MessageChain
        ):
            if all([
                waiter_group.id == group.id,
                waiter_member.id == member.id,
                waiter_message.asDisplay() == "/confirm"
            ]):
                return event
        await inc.wait(waiter)
        await app.sendFriendMessage(member.id, MessageChain.create([
            Plain("请输入学号.")
        ]))

        @Waiter.create_using_function([FriendMessage])
        def waiter(
            event: FriendMessage, waiter_member: Friend, waiter_message: MessageChain
        ):
            if all([
                waiter_member.id == member.id,
            ]):
                id = waiter_message.asDisplay()
                return event
        await inc.wait(waiter)
        await app.sendFriendMessage(member.id, MessageChain.create([
            Plain("请输入密码.")
        ]))

        @Waiter.create_using_function([FriendMessage])
        def waiter(
            event: FriendMessage, waiter_member: Friend, waiter_message: MessageChain
        ):
            if all([
                waiter_member.id == member.id,
            ]):
                return event
        password = message.asDisplay()
        await inc.wait(waiter)
        await app.sendFriendMessage(member.id, MessageChain.create([
            Plain("学号为：" + id + "\n密码为：" + password)
        ]))
        return
    '''

    if (member.id != 349468958):
        msg = message.asSerializationString()
        if(atme(msg)):
            message_a = MessageChain(__root__=[
                Plain("消息监听：\n" + member.name + '(' + str(member.id) + ")在" + group.name + '(' + str(group.id) + ")中可能提到了我：\n")])
            message_b = message.asSendable()
            message_a.plus(message_b)
            await app.sendGroupMessage(mygroup, message_a)

    if member.id == 349468958 and message.asDisplay().startswith("bilibili"):
        await bilibili(app, group, message.asDisplay())

    if message.asDisplay().startswith("switch "):
        await switch(app, group, member, message.asDisplay())

    if (int(read_from_ini('data/switch.ini', str(group.id), 'on', '0')) == 0):
        return
    if message.has(Quote):
        for at in message.get(Quote):
            if at.senderId != app.connect_info.account:
                break
            for msg in message.get(Plain):
                msg.text = msg.text.replace(' ', '')
                if msg.text == '':
                    continue
                if msg.text == 'recall':
                    flag = permissionCheck(member.id, group.id)
                    if flag > 0:
                        print(at.id)
                        await app.revokeMessage(at.id)
                        return

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

    # FIXME 该处权限增加代码可能存在问题，待处理
    if msg.startswith("set ") or msg.startswith("off "):
        await setMain(app, member, group, msgs)

    if (message.asDisplay() == '?' or message.asDisplay() == '？' or
        message.asDisplay() == '草' or message.asDisplay() == '艹' or
            message.asDisplay() == '[图片]'):
        flag = random.randint(0, 99)
        num = random.randint(5, 94)
        if(abs(flag - num) <= 5):
            await app.sendGroupMessage(group, message.asSendable())

    # TODO 实装通过bigfun实现的会战信息查询系统
    if int(read_from_ini('data/switch.ini', str(group.id), 'pcrteam', '0')) == 1 and msg.startswith("pcrteam."):
        await pcrteam(app, group, msg)
    if (msg.startswith("pcr.")):
        await pcr(app, group, msg)
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
        global sess
        try:
            if not member.id in sess:
                temp = createlink(member.id)
                sess[member.id] = temp
            await canvas(app, group, member, msg, sess[member.id])
        except:
            await app.sendGroupMessage(group, MessageChain.create([Plain(
                '并没有记录任何学号信息，如需使用此功能请私聊向bot申请。\n注意：该功能需要用户提供统一身份认证的学号和密码以登录canvas。'
            )]))

    # TODO 天气爬取
    if msg.startswith('weather'):
        await weather(app, inc, group, member, msg)

    # TODO 4m3和1块钱公告爬取

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
        await seImage(app, group, msg)
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
    if (int(read_from_ini('data/switch.ini', str(event.member.group.id), 'on', '0')) == 0):
        return

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
    if (int(read_from_ini('data/switch.ini', str(event.member.group.id), 'on', '0')) == 0):
        return

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
    if event.durationSeconds < 3600:
        return
    await app.quit(event.operator.group)
    # TODO 黑名单系统
    await app.sendGroupMessage(mygroup, MessageChain.create([Plain(
        "在" + event.operator.group.name + '(' + str(event.group.id) + ')被' +
        event.operator.name + '(' + str(event.operator.id) + ')禁言' + time_to_str(event.durationSeconds) +
        '，已自动从群聊中退出并将所在群和禁言人列入黑名单')]))


@bcc.receiver(BotLeaveEventKick)
async def bot_kicked_hanler(app: GraiaMiraiApplication, event: BotLeaveEventKick):
    # TODO 黑名单系统
    await app.sendGroupMessage(mygroup, MessageChain.create([Plain(
        "在" + event.group.name + '(' + str(event.operator.group.id) + ')被移出群聊，已将群和操作人列入黑名单')]))


@bcc.receiver(ApplicationLaunched)
async def repeattt(app: GraiaMiraiApplication):
    # TODO 实装整点报时之类的功能
    asyncio.create_task(clock(app))
    pass

app.launch_blocking()
