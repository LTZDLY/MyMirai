
from graia.ariadne.entry import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.ini import write_in_ini
from function.permission import permissionCheck


async def switch(app, group: Group, sender: Member, message: str):
    msg = message.split()
    if(len(msg) != 3):
        return
    flag = permissionCheck(sender.id, group.id)
    if(msg[1] == 'bot' and flag >= 2):
        await switchMain(app, group, msg[2])
    elif(msg[1] == 'pcrteam' and flag >= 1):
        await switchPcr(app, group, msg[2])


async def switchMain(app, group: Group, switch: str):
    msg = ''
    if switch == 'on':
        write_in_ini('data/switch.ini', str(group.id), 'on', '1')
        msg = '起床咯切噜！'
    elif switch == 'off':
        write_in_ini('data/switch.ini', str(group.id), 'on', '0')
        msg = '要睡咯切噜噜~...'
    elif switch == 'quit':
        await app.send_group_message(group, MessageChain([Plain('切噜走啦，拜拜！~')]))
        await app.quit(group)
    else:
        return
    await app.send_group_message(group, MessageChain(__root__=[Plain(msg)]))


async def switchPcr(app, group: Group, switch: str):
    msg = ''
    if switch == 'on':
        write_in_ini('data/switch.ini', str(group.id), 'pcrteam', '1')
        msg = 'PCR团队战功能开启'
    elif switch == 'off':
        write_in_ini('data/switch.ini', str(group.id), 'pcrteam', '0')
        msg = 'PCR团队战功能关闭'
    else:
        return
    await app.send_group_message(group, MessageChain(__root__=[Plain(msg)]))
