from typing import Union

# from graia.ariadne.app import Ariadne
from graia.ariadne.entry import Friend, Group, Member
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop

from function import ini, permission


def check_ban():
    async def check_ban_deco(member: Member, group: Group):
        if permission.inban(member.id, group.id):
            raise ExecutionStop
    return Depend(check_ban_deco)


def check_group():
    async def check_group_deco(group: Group):
        if int(ini.read_from_ini("data/switch.ini", str(group.id), "on", "0")) == 0:
            raise ExecutionStop

    return Depend(check_group_deco)


# fre = deque()

# def check_frequent(size: int):
#     async def check_frequent_deco(app: Ariadne):
#         print(fre)
#         if len(fre) != 0:
#             first_element = fre[0]
#             now = time.time()
#             if now - first_element < 10:
#                 raise ExecutionStop
#         elif len(fre) >= size:
#             first_element = fre[0]
#             last_element = fre[-1]
#             if last_element - first_element < 60:
#                 raise ExecutionStop
#             fre.popleft()
#     return Depend(check_frequent_deco)


def nothost(*members: int):
    async def check_host(member: Union[Member, Friend]):
        if member.id in members:
            raise ExecutionStop

    return Depend(check_host)


def fromhost(*friends: int):
    async def check_ishost(friend: Union[Member, Friend]):
        if friend.id not in friends:
            raise ExecutionStop

    return Depend(check_ishost)


def check_permission(persion: int):
    async def check_permission_deco(group: Group, member: Member):
        if persion > permission.permissionCheck(member.id, group.id):
            raise ExecutionStop

    return Depend(check_permission_deco)
