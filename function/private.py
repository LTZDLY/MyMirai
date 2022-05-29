from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.mute import set_mute

hostqq = 349468958


def takeSecond(elem):
    return elem.name


async def priv_get(app):
    l = list(await app.getGroupList())
    l.sort(key=takeSecond)
    s = '获取群列表：'
    m = len(l)
    num = 0
    while(m > 0):
        if m > 15:
            n = 15
        else:
            n = m
        m -= n
        for i in range(n):
            if s != '':
                s += '\n'
            s += 'id=' + str(num + i) + '  ' + \
                l[num + i].name + '(' + str(l[num + i].id) + ')'
        print(s)
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain(s)]))
        num += n
        s = ''


async def priv_se(app, message: MessageChain):
    l = await app.getGroupList()
    l.sort(key=takeSecond)
    ss = message.asDisplay().split(' ')
    if (len(ss) != 3):
        return
    if (int(ss[1]) < 0 or int(ss[1]) > len(l) - 1):
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('id错误')]))
        return
    msga = message
    msga.__root__[1].text = msga.__root__[1].text.split(' ')[2]
    try:
        await app.sendGroupMessage(l[int(ss[1])], msga.asSendable())
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('发送成功')]))
    except:
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('发送失败')]))


async def priv_mute(app, message: MessageChain):
    l = await app.getGroupList()
    l.sort(key=takeSecond)
    ss = message.asDisplay().split(' ')
    if (len(ss) != 4):
        return
    if (int(ss[1]) < 0 or int(ss[1]) > len(l) - 1):
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('id错误')]))
        return
    mem = int(ss[2])
    t = float(ss[3])
    try:
        await set_mute(app, l[int(ss[1])], [mem], t)
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('操作成功')]))
    except:
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('操作失败')]))


async def priv_toqq(app, message: MessageChain):
    ss = message.asDisplay().split(' ')
    if (len(ss) != 3):
        return
    msga = message
    msga.__root__[1].text = msga.__root__[1].text.split(' ')[2]
    try:
        await app.sendFriendMessage(int(ss[1]), msga.asSendable())
        await app.sendFriendMessage(hostqq, MessageChain.create([Plain('发送成功')]))
    except:
        try:
            await app.sendTempMessage(int(ss[1]), msga.asSendable())
            await app.sendFriendMessage(hostqq, MessageChain.create([Plain('发送成功')]))
        except:
            await app.sendFriendMessage(hostqq, MessageChain.create([Plain('发送失败')]))


async def priv_handler(app, message: MessageChain):
    if (message.asDisplay() == 'get'):
        await priv_get(app)
    if (message.asDisplay().startswith('se')):
        await priv_se(app, message)
    if (message.asDisplay().startswith('mute')):
        await priv_mute(app, message)
    if (message.asDisplay().startswith('toQQ')):
        await priv_toqq(app, message)
