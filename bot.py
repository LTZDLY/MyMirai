import asyncio
import datetime
import operator
import random
from re import escape
from typing import Optional

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
from function.cherugo import cheru2str, str2cheru
from function.image import seImage
from function.ini import read_from_ini, write_in_ini
from function.mute import mute_member, time_to_str
from function.permission import permissionCheck, setMain
from function.repeat import repeat
from function.signup import (atme, choice, define, loadDefine, paraphrase,
                             signup)
from function.switch import switch

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
    if (member.id == 34946895888):
        flag = random.randint(0, 99)
        num = random.randint(5, 94)
        if(abs(flag - num) <= 5):
            await app.sendGroupMessage(group, message.asSendable())
    mygroup = 958056260
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
        bilibili(app, group, msg)

    if msg.startswith("switch "):
        asyncio.create_task(switch(app, group, member, msg))

    if msg.startswith("set ") or msg.startswith("off "):
        asyncio.create_task(setMain(app, member, group, msgs))

    if (int(read_from_ini('data/switch.ini', str(group.id), 'on', '0')) == 0):
        return

    # TODO 实装通过bigfun实现的会战信息查询系统
    if int(read_from_ini('data/switch.ini', str(group.id), 'pcrteam', '0')) == 1 and msg.startswith("pcrteam."):
        pcrteam(app, group, msg)
    if (msg.startswith("pcr.")):
        pcr(app, group, msg)
    '''
    if msg == '110':
        message = MessageChain.create([
            Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/99e465b59ddce9410aa8f5ae1a96a17da91736c4.png'),
            Image.fromNetworkAddress('https://i0.hdslb.com/bfs/bigfun/90e102e603c4df5da446c7f9abad014b144f5836.png@150w_1o')
        ])
        await app.sendGroupMessage(group, message)
    '''
    # TODO 实装TouHouRoll机

    if msg == "签到":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(signup(member.id))]))
    # print(await app.getMember(group, 1424912867))
    if member.id == 349468958 and msg.startswith("mute"):
        mute_member(app, group, message.asSerializationString())

    if message.asDisplay().startswith("define "):
        if(permissionCheck(member.id, group.id) == 3):
            define(message.asDisplay())

    if msg.startswith("切噜 "):
        s = msg.replace("切噜 ", '', 1)
        if len(s) > 500:
            msg = '切、切噜太长切不动勒切噜噜...'
        else:
            msg = '切噜～♪' + str2cheru(s)
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(msg)]))
    elif msg.startswith("切噜～♪"):
        s = msg.replace("切噜～♪", '', 1)
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


@bcc.receiver(ApplicationLaunched)
async def repeattt(app: GraiaMiraiApplication):
    # asyncio.create_task(repeat(app))
    pass

app.launch_blocking()
