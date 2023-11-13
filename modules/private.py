import traceback

from graia.ariadne.app import Ariadne
from graia.ariadne.entry import Friend, Member
from graia.ariadne.event.message import FriendMessage, TempMessage
from graia.ariadne.event.mirai import (
    BotInvitedJoinGroupRequestEvent,
    NewFriendRequestEvent,
)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.base import MatchContent, DetectPrefix
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from function import decorators
from function.data import hostqq

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[BotInvitedJoinGroupRequestEvent]))
async def new_group_invited_handler(
    app: Ariadne, event: BotInvitedJoinGroupRequestEvent
):
    try:
        await event.accept()
        if event.supplicant != hostqq:
            await app.send_friend_message(
                hostqq,
                MessageChain(
                    [
                        Plain(
                            f"{event.nickname}({event.supplicant})邀请加入群聊{event.group_name}({event.source_group})，已自动通过。"
                        )
                    ]
                ),
            )
    except Exception as e:
        traceback.print_exc()
        await app.send_friend_message(
            hostqq, MessageChain([Plain(traceback.format_exc())])
        )


@channel.use(ListenerSchema(listening_events=[NewFriendRequestEvent]))
async def new_friend_handler(app: Ariadne, event: NewFriendRequestEvent):
    try:
        await event.accept()
        await app.send_friend_message(
            hostqq,
            MessageChain(
                [
                    Plain(
                        f"{event.nickname}({event.supplicant})申请好友，已自动通过。附加信息如下：\n{event.message}"
                    )
                ]
            ),
        )
    except Exception as e:
        traceback.print_exc()
        await app.send_friend_message(
            hostqq, MessageChain([Plain(traceback.format_exc())])
        )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage], decorators=[decorators.nothost(hostqq)]
    )
)
async def forward_listener(app: Ariadne, message: MessageChain, friend: Friend):
    message_a = MessageChain([Plain("%s(%d)发送消息：\n" % (friend.nickname, friend.id))])
    message_a.extend(message.as_sendable())
    await app.send_friend_message(hostqq, message_a)


@channel.use(
    ListenerSchema(listening_events=[FriendMessage], decorators=[MatchContent("切噜")])
)
async def friend_message_handler(app: Ariadne, friend: Friend):
    await app.send_friend_message(friend, MessageChain([Plain("切噜~♪")]))


@channel.use(
    ListenerSchema(listening_events=[FriendMessage], decorators=[DetectPrefix("echo ")])
)
async def _(app: Ariadne, friend: Friend, message: MessageChain):
    message_a = message
    message_a.__root__[0].text = message_a.__root__[0].text.replace("echo ", "", 1)
    await app.send_friend_message(friend, message_a.as_sendable())


@channel.use(ListenerSchema(listening_events=[TempMessage]))
async def temp_message_handler(app: Ariadne, message: MessageChain, sender: Member):
    message_a = MessageChain([Plain("%s(%d)向您发送消息：\n" % (sender.name, sender.id))])
    message_a.extend(message.as_sendable())
    await app.send_friend_message(hostqq, message_a)
