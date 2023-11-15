import json
from graia.ariadne.entry import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from function.ini import write_in_ini
from function.permission import permissionCheck


async def switch(app, group: Group, sender: Member, message: str):
    msg = message.split()
    if len(msg) != 3:
        return
    flag = permissionCheck(sender.id, group.id)
    if msg[1] == "bot" and flag >= 2:
        await switchMain(app, group, msg[2])
    elif msg[1] == "pcrteam" and flag >= 1:
        await switchPcr(app, group, msg[2])


async def switchMain(app, group: Group, switch: str):
    msg = ""
    if switch == "on":
        write_in_ini("data/switch.ini", str(group.id), "on", "1")
        msg = "起床咯切噜！"
    elif switch == "off":
        write_in_ini("data/switch.ini", str(group.id), "on", "0")
        msg = "要睡咯切噜噜~..."
    elif switch == "quit":
        try:
            await app.send_group_message(group, MessageChain([Plain("切噜走啦，拜拜！~")]))
        except:
            pass
        await app.quit_group(group)
    else:
        return
    await app.send_group_message(group, MessageChain(__root__=[Plain(msg)]))


async def switchPcr(app, group: Group, switch: str):
    msg = ""
    if switch == "on":
        write_in_ini("data/switch.ini", str(group.id), "pcrteam", "1")
        msg = "PCR团队战功能开启"
    elif switch == "off":
        write_in_ini("data/switch.ini", str(group.id), "pcrteam", "0")
        msg = "PCR团队战功能关闭"
    else:
        return
    await app.send_group_message(group, MessageChain(__root__=[Plain(msg)]))


def addBlackList(id, action_type=1):
    """action_type 取1代表用户，取2代表群组"""

    Localpath = "data/blacklist.json"
    bl = ""
    with open(Localpath, "r", encoding="utf8") as fp:
        bl = json.load(fp)
    if action_type == 1:
        bl["member"].append(id)
    elif action_type == 2:
        bl["group"].append(id)

    with open(Localpath, "w", encoding="utf8") as fw:
        jsObj = json.dumps(bl)
        fw.write(jsObj)
        fw.close()


async def checkBlankList(app):
    Localpath = "data/blacklist.json"
    bl = ""
    with open(Localpath, "r", encoding="utf8") as fp:
        bl = json.load(fp)
    fl = bl["member"]
    gl = bl["group"]
    for i in fl:
        f = await app.get_friend(i)
        if f:
            await app.delete_friend(f)
    for i in gl:
        g = await app.get_group(i)
        if g:
            await app.quit_group(g)
