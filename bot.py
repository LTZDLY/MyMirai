import asyncio
from function.bilibili import bilibili
from function.mute import mute_member, time_to_str
from function.repeat import repeat
from function.signup import signup

import operator
import random
import datetime

from typing import Optional

from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.group import Group
from graia.application.group import Member
from graia.application.friend import Friend
from graia.broadcast import Broadcast

from graia.application.message.elements.internal import Plain

from graia.application.entry import FriendMessage
from graia.application.entry import GroupMessage
from graia.application.entry import MemberMuteEvent
from graia.application.entry import MemberUnmuteEvent
from graia.application.entry import BotMuteEvent
from graia.application.event.lifecycle import ApplicationLaunched


loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080",  # 填入 httpapi 服务运行的地址
        authKey="LTZDLYLLS",  # 填入 authKey
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
    if (member.id == 349468958):
        flag = random.randint(0, 99)
        num = random.randint(5, 94)
        if(abs(flag - num) <= 5):
            await app.sendGroupMessage(group, message.asSendable())
    if message.asDisplay() == "签到":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(signup(member.id))]))
    # print(await app.getMember(group, 1424912867))
    if member.id == 349468958 and message.asDisplay().startswith("bilibili"):
        bilibili(app, group, message.asDisplay())
    if member.id == 349468958 and message.asDisplay().startswith("mute"):
        mute_member(app, group, message.asSerializationString())


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
