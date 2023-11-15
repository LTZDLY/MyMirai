import asyncio
import json
from functools import partial

from graia.ariadne.app import Ariadne
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.mirai import (
    BotLeaveEventKick,
    BotMuteEvent,
    MemberMuteEvent,
    MemberUnmuteEvent,
)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from function import bilibili, danmaku, ini, mute, repeat, switch
from function.data import hostqq, live, mygroup, mytasks

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MemberMuteEvent]))
async def member_mute_handler(app: Ariadne, event: MemberMuteEvent):
    return
    if (
        int(ini.read_from_ini("data/switch.ini", str(event.member.group.id), "on", "0"))
        == 0
    ):
        return

    if event.operator is None:
        return
    sstr = mute.time_to_str(event.duration)
    # print(sstr)
    message = MessageChain(
        [
            Plain(
                "%s(%d)被%s(%d)禁言%s"
                % (
                    event.member.name,
                    event.member.id,
                    event.operator.name,
                    event.operator.id,
                    sstr,
                )
            )
        ]
    )
    await app.send_group_message(event.member.group.id, message)
    # print(MemberMuteEvent.duration)


@channel.use(ListenerSchema(listening_events=[MemberUnmuteEvent]))
async def member_unmute_handler(app: Ariadne, event: MemberUnmuteEvent):
    return
    if (
        int(ini.read_from_ini("data/switch.ini", str(event.member.group.id), "on", "0"))
        == 0
    ):
        return

    if event.operator is None:
        return
    message = MessageChain(
        [
            Plain(
                "%s(%d)被%s(%d)解除禁言"
                % (
                    event.member.name,
                    event.member.id,
                    event.operator.name,
                    event.operator.id,
                )
            )
        ]
    )
    await app.send_group_message(event.member.group.id, message)
    # app.getMember()


@channel.use(ListenerSchema(listening_events=[BotMuteEvent]))
async def bot_mute_handler(app: Ariadne, event: BotMuteEvent):
    if event.operator.id == hostqq:
        return
    if event.duration <= 3600:
        return
    # TODO 黑名单系统
    switch.addBlackList(event.operator.id)
    switch.addBlackList(event.operator.group, 2)
    await app.quit_group(event.operator.group)
    await app.send_group_message(
        mygroup,
        MessageChain(
            [
                Plain(
                    "在%s(%d)被%s(%d)禁言%s，已自动从群聊中退出并将所在群和禁言人列入黑名单"
                    % (
                        event.operator.group.name,
                        event.operator.group.id,
                        event.operator.name,
                        event.operator.id,
                        mute.time_to_str(event.duration),
                    )
                )
            ]
        ),
    )


@channel.use(ListenerSchema(listening_events=[BotLeaveEventKick]))
async def bot_kicked_hanler(app: Ariadne, event: BotLeaveEventKick):
    # TODO 黑名单系统
    switch.addBlackList(event.operator.id)
    switch.addBlackList(event.operator.group, 2)
    await app.send_group_message(
        mygroup,
        MessageChain(
            [
                Plain(
                    "在%s(%d)被%s(%d)移出群聊，已将群和操作人列入黑名单"
                    % (
                        event.operator.group.name,
                        event.operator.group.id,
                        event.operator.name,
                        event.operator.id,
                    )
                )
            ]
        ),
    )


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def repeattt(app: Ariadne):
    # 这段的逻辑需要修改
    # 现在的逻辑是，开机时检测是否完成初始化，若无则进行初始化
    # 应修改成的逻辑是：
    # 开机时不需要额外检查是否初始化。在执行过程中发现若未完成初始化则进行
    # 已修改完成
    # Localpath = './data/cookies.json'
    # with open(Localpath, 'r', encoding='utf8')as fp:
    #     cookies = json.load(fp)
    # settings = cookies['settings']
    # for i in settings:
    #     if settings[i] == 1:
    #         asyncio.create_task(private_msg_init(app, cookies[i]))

    # TODO 实装整点报时之类的功能

    # 整点任务在开机时完成初始化
    # 将需要整点执行的任务作为lambda表达式加入mytasks字典当中
    Localpath = "./data/cookies.json"
    with open(Localpath, "r", encoding="utf8") as fp:
        cookies = json.load(fp)
    settings = cookies["settings"]
    for i in settings:
        # 此时i代表部门名
        if settings[i] == 1:
            mytasks[i] = partial(bilibili.getprivate, app, i)

    asyncio.create_task(repeat.clock(app, mytasks))
    # asyncio.create_task(repeat.clock_test(app))

    Localpath = "./data/live.json"
    data = {}
    fr = open(Localpath, encoding="utf-8")
    data = json.load(fr)
    fr.close()

    for i in data["data"]:
        live[str(i["room_id"])] = asyncio.create_task(
            danmaku.entrence(app, str(i["room_id"]))
        )
