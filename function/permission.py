import json
import os
from typing import Dict

from graia.ariadne.entry import Group, Member


def inban(member: int = None, group: int = None) -> bool:
    Localpath = "./data/blacklist.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    if "member" in data and member in data["member"]:
        return True
    if "group" in data and group in data["group"]:
        return True
    return False


def loadPermission():
    Localpath = "./data/data.json"
    data = {}
    if os.path.exists(Localpath) == False:
        return {"AAOP": [349468958], "AOP": [], "OP": {}}
    else:
        fr = open(Localpath, encoding="utf-8")
        data = json.load(fr)
        fr.close()
        if not ("Permission" in data):
            return {"AAOP": [349468958], "AOP": [], "OP": {}}
    return data["Permission"]


def permissionCheck(member: int, group: int) -> int:
    """对发送者以及所在群进行权限检查

    Returns:
        int:
           -1: 在黑名单中的群员//还没写
            0: 不拥有权限的群员
            1: 具有一般权限的群员
            2: 具有高级权限的群员
            3: 具有最高级权限的群员
    """
    per = loadPermission()
    if member in per["AAOP"]:
        return 3
    if member in per["AOP"]:
        return 2
    if str(group) in per["OP"]:
        if member in per["OP"][str(group)]:
            return 1
    return 0


async def setMain(app, member: Member, group: Group, message: str):
    Localpath = "./data/data.json"
    """
    data = {}
    if os.path.exists(Localpath) == False:
        data = {"Permission": {"AAOP": [349468958], "AOP": [], "OP": {}}}
        data['Permission']['AOP']
    else:
        fr = open(Localpath)
        data = json.load(fr)
        fr.close()
        if not('Permission' in data):
            data_new = {"Permission": {
                "AAOP": [349468958], "AOP": [], "OP": {}}}
            for i in data_new:
                data[i] = data_new[i]
    print(data)

    jsObj = json.dumps(data)
    with open(Localpath, "w", encoding='utf8') as fw:
        fw.write(jsObj)
        fw.close()
    """

    if message.find("[mirai:at:") == -1:
        return
    flag = permissionCheck(member.id, group.id)
    if flag <= 1:
        return
    setlist = []
    prem = ""
    text = message.split(" ")
    if len(text) <= 2:
        return
    text[0] = text[0][text[0].find("]") + 1 :]
    for sstr in text[1:]:
        if sstr.startswith("[mirai:at:"):
            ssstr = sstr.split(",")
            setlist.append(int(ssstr[0][10:]))
        else:
            prem = sstr
    data = loadPermission()
    print(data)
    if text[0].startswith("set"):
        if prem == "OP" and flag >= 2:
            for i in setlist:
                if permissionCheck(i, group.id) >= 1:
                    continue
                if str(group.id) in data["OP"]:
                    for i in setlist:
                        data["OP"][str(group.id)].append(i)
                else:
                    data_new = {str(group.id): setlist}
                    for i in data_new:
                        data["OP"][i] = data_new[i]
        if prem == "AOP" and flag >= 3:
            for i in setlist:
                if permissionCheck(i, group.id) >= 2:
                    continue
                data["AOP"].append(i)
    elif text[0].startswith("off"):
        if prem == "OP" and flag >= 2:
            for i in setlist:
                if permissionCheck(i, group.id) != 1:
                    continue
                else:
                    data["OP"][str(group.id)].remove(i)
        if prem == "AOP" and flag >= 3:
            for i in setlist:
                if permissionCheck(i, group.id) != 2:
                    continue
                else:
                    data["AOP"].remove(i)

    if os.path.exists(Localpath) == False:
        jsObj = {"Permission": data}
        jsObj = json.dumps(jsObj, ensure_ascii=False)
        with open(Localpath, "w", encoding="utf8") as fw:
            fw.write(jsObj)
            fw.close()
    else:
        fr = open(Localpath, encoding="utf-8")
        jsObj = json.load(fr)
        fr.close()
        data_new = {"Permission": data}
        for i in data_new:
            jsObj[i] = data_new[i]
        with open(Localpath, "w", encoding="utf8") as fw:
            jsObj = json.dumps(jsObj)
            fw.write(jsObj)
            fw.close()
