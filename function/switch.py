
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from function.ini import write_in_ini
from function.permission import permissionCheck


async def switch(app, group: Group, sender: Member, message: str):
    msg = message.split()
    print(msg)
    if(len(msg) != 3):
        return
    flag = permissionCheck(sender.id, group.id)
    if(msg[1] == 'bot' and flag >= 2):
        await switchMain(app, group, msg[2])

async def switchMain(app, group: Group, switch: str):
    msg = ''
    if switch == 'on':
        write_in_ini('data/switch.ini', str(group.id), 'on', '1')
        msg = '起床咯切噜！'
    elif switch == 'off':
        write_in_ini('data/switch.ini', str(group.id), 'on', '0')
        msg = '要睡咯切噜噜~...'
    else:
        return
    await app.sendGroupMessage(group, MessageChain(__root__=[Plain(msg)]))
