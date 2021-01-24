import asyncio
import datetime
import json
import operator
import random
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
from function.canvas import add_person, canvas, createlink
from function.cherugo import cheru2str, str2cheru
from function.danmaku import danmaku, startup
from function.image import seImage
from function.ini import read_from_ini, write_in_ini
from function.latex import latex
from function.leetcode import get_daily, get_rand
from function.mute import mute_member, set_mute, time_to_str
from function.pcr import pcr, pcrteam
from function.permission import inban, permissionCheck, setMain
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
        Plain(sender.name + '(' + str(sender.id) + ')' + "向您发送消息：\n")])
    message_b = message.asSendable()
    message_a.plus(message_b)
    await app.sendFriendMessage(349468958, message_a)

ti = 0


@bcc.receiver(GroupMessage)
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    if inban(member.id, group.id):
        return
    permissionflag = permissionCheck(member.id, group.id)
    # FIXME 用户向bot提供学号和密码用于登录canvas爬取数据
    if message.asDisplay() == "help":
        sstr = "功能列表：" + \
            "\n目前可以公开使用的模块有：" +\
            "\n切噜：切噜语加密\\解密" +\
            "\npcr：pcr模块" +\
            "\npcrteam：pcr团队战模块" +\
            "\n天气：天气模块" +\
            "\n来点：图库模块" +\
            "\nmute：禁言模块" +\
            "\n不可以公开使用的模块有：" +\
            "\nbilibili：bilibili模块" +\
            "\ncanvas：canvas模块" +\
            "\ndanmaku：弹幕姬模块" +\
            "\nswitch：开关模块" +\
            "\ndefine：转义模块" +\
            "\ntimer：报时模块"
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(sstr)
        ]))
        return
    if message.asDisplay().startswith("canvas.apply"):
        Localpath = './data/tongji.json'
        data = {}
        fr = open(Localpath, encoding='utf-8')
        data = json.load(fr)
        fr.close()

        for i in data["data"]:
            if i['qq'] == member.id:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id), Plain("您已在列表当中！")
                ]))
                break
        else:
            try:
                await app.sendFriendMessage(member.id, MessageChain.create([
                    Plain("您即将向bot申请canvas爬取权限。这意味着：\n" +
                          "您需要将自己统一身份认证的学号以及密码私聊发送至bot\n" +
                          "我们可以保证您的学号和密码不会用于爬取canvas数据以外的地方\n" +
                          "如果您确定要申请此功能，请向bot私聊发送 /confirm 以继续运行\n")
                ]))
            except:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id), Plain("您并不是bot好友！")
                ]))

            global ti
            ti = 0

            @Waiter.create_using_function([FriendMessage], block_propagation=True)
            async def waiter(event: FriendMessage, waiter_member: Friend, waiter_message: MessageChain):
                global ti
                if ti != 0:
                    return event
                if waiter_member.id == member.id:
                    if waiter_message.asDisplay() != "/confirm":
                        await app.sendFriendMessage(member.id, MessageChain.create([
                            Plain("您取消了申请.")
                        ]))
                        return event
                    await app.sendFriendMessage(member.id, MessageChain.create([
                        Plain("请输入学号.")
                    ]))
                    ti += 1

                    @Waiter.create_using_function([FriendMessage], block_propagation=True)
                    async def waiter1(event1: FriendMessage, waiter1_member: Friend, waiter1_message: MessageChain):
                        global ti
                        if ti != 1:
                            return event
                        if waiter1_member.id == member.id:
                            await app.sendFriendMessage(member.id, MessageChain.create([
                                Plain("请输入密码.")
                            ]))
                            ti += 1

                            @Waiter.create_using_function([FriendMessage], block_propagation=True)
                            async def waiter2(event2: FriendMessage, waiter2_member: Friend, waiter2_message: MessageChain):
                                global ti
                                if ti != 2:
                                    return event
                                if waiter2_member.id == member.id:
                                    id = int(waiter1_message.asDisplay())
                                    password = waiter2_message.asDisplay()
                                    try:
                                        add_person(
                                            waiter2_member.id, id, password)
                                        await app.sendFriendMessage(member.id, MessageChain.create([
                                            Plain("记录成功.")
                                        ]))
                                    except:
                                        await app.sendFriendMessage(member.id, MessageChain.create([
                                            Plain("记录失败，请检查学号密码是否正确.")
                                        ]))
                                    return event
                            await inc.wait(waiter2)
                            return event
                    await inc.wait(waiter1)
                    return event
            await inc.wait(waiter)
            return

    if (member.id != 349468958):
        msg = message.asSerializationString()
        if(atme(msg)):
            message_a = MessageChain(__root__=[
                Plain("消息监听：\n" + member.name + '(' + str(member.id) + ")在" + group.name + '(' + str(group.id) + ")中可能提到了我：\n")])
            message_b = message.asSendable()
            message_a.plus(message_b)
            for i in range(0,len(message_a.__root__)):
                if message_a.__root__[i].type == 'At':
                    message_a.__root__[i] = Plain(message_a.__root__[i].display)
            await app.sendGroupMessage(mygroup, message_a)

    if member.id == 349468958 and message.asDisplay().startswith("bilibili"):
        await bilibili(app, group, message.asDisplay())

    if message.asDisplay().startswith("switch "):
        await switch(app, group, member, message.asDisplay())

    if (int(read_from_ini('data/switch.ini', str(group.id), 'on', '0')) == 0):
        return
    if message.has(Quote):
        for at in message.get(Quote):
            for msg in message.get(Plain):
                msg.text = msg.text.replace(' ', '')
                if msg.text == '':
                    continue
                if msg.text == 'recall':
                    flag = permissionCheck(member.id, group.id)
                    if flag > 0:
                        await app.revokeMessage(at.id)
                        await app.revokeMessage(message.__root__[0].id)
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
        message.asDisplay() == '草' or message.asDisplay() == '艹'):
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
    if msg.startswith('canvas.'):
        global sess
        try:
            if not member.id in sess:
                temp = createlink(member.id)
                sess[member.id] = temp
            await canvas(app, group, member, msg, sess[member.id])
        except:
            await app.sendGroupMessage(group, MessageChain.create([Plain(
                '并没有记录任何学号信息，如需使用此功能请在群内发送 canvas.apply 以向bot申请。\n' +
                '注意：在此之前请检查您是否与bot互为好友'
            )]))

    # TODO 天气爬取
    if msg.split(' ')[0].endswith('天气'):
        await weather(app, inc, group, member, msg)

    # TODO 4m3和1块钱公告爬取

    if member.id == 349468958 and msg.startswith("danmaku.end"):
        t = a.get((group.id, member.id), None)
        if t:
            t.cancel()
            await app.sendGroupMessage(group, MessageChain.create([Plain("直播视奸停止")]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([At(349468958), Plain("你并没有在视奸")]))

    # TODO leetcode爬取
    if msg == "leetcode.daily":
        await get_daily(app, group)
    if msg == "leetcode.rand":
        await get_rand(app, group)
    if msg == "签到":
        await app.sendGroupMessage(group, MessageChain(__root__=[Plain(signup(member.id))]))
    # print(await app.getMember(group, 1424912867))
    if permissionflag >= 1 and msg.startswith("mute"):
        mute_member(app, group, message)

    if msg.startswith("latex "):
        await latex(app, group, msg)

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
    if msg.find("/生日快乐") != -1 and len(msg.replace("/生日快乐", "")) == 0:
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
        if message.asDisplay().find("/生日快乐") != -1:
            try:
                await set_mute(app, group, [member.id], 600)
            except:
                pass 
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
    if event.durationSeconds <= 3600:
        return
    # TODO 黑名单系统
    await app.sendGroupMessage(mygroup, MessageChain.create([Plain(
        "在" + event.operator.group.name + '(' + str(event.operator.group.id) + ')被' +
        event.operator.name + '(' + str(event.operator.id) + ')禁言' + time_to_str(event.durationSeconds) +
        '，已自动从群聊中退出并将所在群和禁言人列入黑名单')]))
    await app.quit(event.operator.group)


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
