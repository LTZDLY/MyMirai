import asyncio
import datetime
import json
import os
import traceback

from graia.ariadne.app import Ariadne
from graia.ariadne.entry import Group, Member
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Quote
from graia.ariadne.message.parser.base import ContainKeyword
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from function import bilibili, danmaku, decorators, excel, permission, private
from function.data import hostqq, live, mytasks

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage], decorators=[decorators.fromhost(hostqq)]
    )
)
async def friendmsg_listener(app: Ariadne, message: MessageChain):
    # # TODO 移植cq中最高权限的私聊指令
    await private.priv_handler(app, message)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[ContainKeyword("recall"), decorators.fromhost(hostqq)],
    )
)
async def recall_listener(app: Ariadne, message: MessageChain, group: Group):
    # bot撤回指令
    print(message)
    print(message.__root__)
    print(message.as_persistent_string())
    
    print("aadfadsfa")
    if message.has(Quote):
        print("hasquote")
        for at in message.get(Quote):
            print(at)
            await app.recall_message(at.id, group)
            await app.recall_message(message, group)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[decorators.fromhost(hostqq)],
    )
)
async def fun(app: Ariadne, message: MessageChain, member: Member, group: Group):
    if member.id == hostqq and message.display == "生日测试":
        await excel.readexcel(app, 958056260)

    # 权限增删
    if message.display.startswith("set ") or message.display.startswith("off "):
        await permission.setMain(app, member, group, message.display)

    if message.display == "检查监听":
        num = len(live)
        dnum = 0
        for i, j in live.items():
            print(i, j)
            if j.done():
                dnum += 1
                live[i] = asyncio.create_task(danmaku.entrence(app, i))
        if dnum:
            await app.send_group_message(
                group,
                MessageChain(
                    [Plain(f"一共有{num}个直播间在被监听，其中{dnum}个直播间的监听发生中断，已进行重启")]
                ),
            )
        else:
            await app.send_group_message(
                group, MessageChain([Plain(f"一共有{num}个直播间在被监听，一切正常")])
            )

    if message.display == "重置监听":
        num = len(live)
        for i, j in live.items():
            live[i].cancel()
            live[i] = asyncio.create_task(danmaku.entrence(app, i))
        await app.send_group_message(
            group, MessageChain([Plain(f"{num}个直播间已进行重启")])
        )

    if message.display == "packup":
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        os.makedirs(f"./data/{date}/")
        try:
            await excel.packup(app, group.id, date)
            await app.send_group_message(group, MessageChain([Plain("备份群成员信息成功")]))
        except:
            await app.send_group_message(group, MessageChain([Plain("备份群成员信息失败")]))
            traceback.print_exc()
            await app.send_group_message(
                group, MessageChain([Plain(traceback.format_exc())])
            )

    if message.display == "packupall":
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        os.makedirs(f"./data/{date}/")
        try:
            my_list = await app.get_group_list()
            for i in my_list:
                await excel.packup(app, i.id, date)
            await app.send_group_message(
                group, MessageChain([Plain("备份所有群成员信息成功")])
            )
        except:
            await app.send_group_message(
                group, MessageChain([Plain("备份所有群成员信息失败")])
            )
            traceback.print_exc()
            await app.send_group_message(
                group, MessageChain([Plain(traceback.format_exc())])
            )

    # 测试拉取
    if message.display.startswith("测试拉取"):
        sstr = message.display.split(" ", 2)
        if len(sstr) < 2:
            await app.send_group_message(group, MessageChain([Plain("缺少参数")]))
        else:
            Localpath = "./data/cookies.json"
            with open(Localpath, "r", encoding="utf8") as fp:
                cookies = json.load(fp)
            data = cookies[sstr[1]]
            print(f"{sstr[1]}正在进行消息拉取...")
            msg_list = await bilibili.private_msg(app, data)
            if msg_list:
                await app.send_group_message(group, msg_list)
            else:
                await app.send_group_message(
                    group, MessageChain([Plain(f"{sstr[1]}没有拉取到东西")])
                )

    if message.display.startswith("测试全拉取"):
        for i in mytasks:
            asyncio.create_task(mytasks[i]())

    if message.display == "打印任务":
        print(mytasks)
        await app.send_group_message(group, MessageChain([Plain(str(mytasks))]))
    if message.display == "执行任务":
        for i in mytasks:
            asyncio.create_task(mytasks[i]())
