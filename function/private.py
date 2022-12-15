from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.ini import write_in_ini
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
    while (m > 0):
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
        await app.sendFriendMessage(hostqq, MessageChain([Plain(s)]))
        num += n
        s = ''


async def priv_se(app, message: MessageChain):
    l = await app.getGroupList()
    l.sort(key=takeSecond)
    ss = message.display.split(' ')
    if (len(ss) != 3):
        return
    if (int(ss[1]) < 0 or int(ss[1]) > len(l) - 1):
        await app.sendFriendMessage(hostqq, MessageChain([Plain('id错误')]))
        return
    msga = message
    msga.__root__[1].text = msga.__root__[1].text.split(' ')[2]
    try:
        await app.send_group_message(l[int(ss[1])], msga.asSendable())
        await app.sendFriendMessage(hostqq, MessageChain([Plain('发送成功')]))
    except:
        await app.sendFriendMessage(hostqq, MessageChain([Plain('发送失败')]))


async def priv_mute(app, message: MessageChain):
    l = await app.getGroupList()
    l.sort(key=takeSecond)
    ss = message.display.split(' ')
    if (len(ss) != 4):
        return
    if (int(ss[1]) < 0 or int(ss[1]) > len(l) - 1):
        await app.sendFriendMessage(hostqq, MessageChain([Plain('id错误')]))
        return
    mem = int(ss[2])
    t = float(ss[3])
    try:
        await set_mute(app, l[int(ss[1])], [mem], t)
        await app.sendFriendMessage(hostqq, MessageChain([Plain('操作成功')]))
    except:
        await app.sendFriendMessage(hostqq, MessageChain([Plain('操作失败')]))


async def priv_toqq(app, message: MessageChain):
    ss = message.display.split(' ')
    if (len(ss) != 3):
        return
    msga = message
    msga.__root__[1].text = msga.__root__[1].text.split(' ')[2]
    try:
        await app.sendFriendMessage(int(ss[1]), msga.asSendable())
        await app.sendFriendMessage(hostqq, MessageChain([Plain('发送成功')]))
    except:
        try:
            await app.sendTempMessage(int(ss[1]), msga.asSendable())
            await app.sendFriendMessage(hostqq, MessageChain([Plain('发送成功')]))
        except:
            await app.sendFriendMessage(hostqq, MessageChain([Plain('发送失败')]))


async def priv_switch(app, message: MessageChain):
    # switch [id] [on/off/quit]
    ss = message.display.split(' ')
    if (len(ss) != 3):
        return
    l = await app.getGroupList()
    l.sort(key=takeSecond)
    if (int(ss[1]) < 0 or int(ss[1]) > len(l) - 1):
        await app.sendFriendMessage(hostqq, MessageChain([Plain('id错误')]))
        return
    switch = ss[2]
    if switch == 'on':
        write_in_ini('data/switch.ini', str(l[int(ss[1])].id), 'on', '1')
        await app.sendFriendMessage(hostqq, MessageChain([Plain(f'启用切噜在{l[int(ss[1])].name}')]))
    elif switch == 'off':
        write_in_ini('data/switch.ini', str(l[int(ss[1])].id), 'on', '0')
        await app.sendFriendMessage(hostqq, MessageChain([Plain(f'关闭切噜在{l[int(ss[1])].name}')]))
    elif switch == 'quit':
        await app.sendFriendMessage(hostqq, MessageChain([Plain(f'退出切噜在{l[int(ss[1])].name}')]))
        await app.quit_group(l[int(ss[1])])


async def priv_find(app, message: MessageChain):
    # find [kw]
    ss = message.display.split(' ', 1)
    if (len(ss) < 2):
        return
    l = list(await app.getGroupList())
    l.sort(key=takeSecond)
    s = '获取群列表：'
    for i in range(len(l)):
        if l[i].name.find(ss[1]) != -1:
            if s != '':
                s += '\n'
            s += 'id=' + str(i) + '  ' + \
                l[i].name + '(' + str(l[i].id) + ')'
    print(s)
    await app.sendFriendMessage(hostqq, MessageChain([Plain(s)]))


async def priv_handler(app, message: MessageChain):
    if (message.display == 'get'):
        await priv_get(app)
    if (message.display.startswith('se')):
        await priv_se(app, message)
    if (message.display.startswith('mute')):
        await priv_mute(app, message)
    if (message.display.startswith('toQQ')):
        await priv_toqq(app, message)
    if (message.display.startswith('switch')):
        await priv_switch(app, message)
    if (message.display.startswith('find')):
        await priv_find(app, message)
