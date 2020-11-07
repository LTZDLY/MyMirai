import asyncio

from graia.application.group import Group, Member, MemberPerm
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Plain


def time_to_str(second: int) -> str:
    minute = 0
    hour = 0
    day = 0
    if (second >= 60):
        minute = second // 60
        second = second % 60
    if (minute >= 60):
        hour = minute // 60
        minute = minute % 60
    if (hour >= 24):
        day = hour // 24
        hour = hour % 24
    # print(day, hour, minute, second)
    sstr = ((str(day) + '天') if (day != 0) else '') + (
        (str(hour) + '小时') if (hour != 0) else '') + (
        (str(minute) + '分钟') if (minute != 0) else '') + (
        (str(second) + '秒') if (second != 0) else '')
    return sstr

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def mute_member(app, group: Group, msg: MessageChain):
    if not msg.has(At):
        return
    mutelist = []
    time = 0
    text = msg.asDisplay().split(' ')
    for at in msg.get(At):
        mutelist.append(at.target)
    for i in text:
        if is_number(i):
            time = max(time, float(i))
    mutelist.sort()
    asyncio.create_task(set_mute(app, group, mutelist, time))


async def set_mute(app, group: Group, mutelist: list, mutetime):
    num = 1
    lenn = len(mutelist)
    # my = await app.getMember(group, 1424912867)
    # my_flag = 1 if my.permission == "MEMBER" else 2 if my.permission == "ADMINISTRATOR" else 3
    my_flag = 3
    for i in range(lenn):
        time = mutetime * 60
        sender: Member
        sender = await app.getMember(group, mutelist[i])
        sender_flag: int
        # print(sender.permission.Member)
        sender_flag = 1 if sender.permission == MemberPerm.Member else 2 if sender.permission == MemberPerm.Administrator else 3
        if(i != lenn - 1):
            if(mutelist[i] == mutelist[i+1]):
                num += 1
                continue
        time = pow(time/60 * num, num) * 60
        num = 1
        if(my_flag > sender_flag):
            if(time > 2592000):
                time = 2592000
            if (time == 0):
                text = sender.name + '(' + str(sender.id) + ')' + \
                    "被我解除禁言"
                await app.unmute(group, sender)
            else:
                text = sender.name + '(' + str(sender.id) + ')' + \
                    "被我禁言" + time_to_str(int(time))
                await app.mute(group, sender, int(time))
            await app.sendGroupMessage(group, MessageChain.create([Plain(text)]))


'''
mmsg = 'mute 1 [mirai:at:349468958,@七曜の筱蓝] [mirai:at:349468958,@七曜の筱蓝] [mirai:at:349468958,@七曜の筱蓝]'
mute_member(mmsg)
'''
