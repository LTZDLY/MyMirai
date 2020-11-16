import os
from pathlib import Path
import random

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Image, Plain


async def seImage(app, group, msg: str):
    message = ''
    filePath = ''
    file = ''
    if(msg.find('小蓝') != -1):
        msg = msg.replace('小蓝', '爱抖露')
        await app.sendGroupMessage(group, MessageChain.create([Plain("已自动进行转义：小蓝->爱抖露")]))
    elif(msg.find('美少女') != -1):
        msg = msg.replace('美少女', '爱抖露')
        await app.sendGroupMessage(group, MessageChain.create([Plain("已自动进行转义：美少女->爱抖露")]))
    if(msg.find('猫') != -1):
        filePath = 'E:/Mirai/mirai/img/cat/'
    elif(msg.find('狗') != -1):
        filePath = 'E:/Mirai/mirai/img/dog/'
    elif(msg.find('色图') != -1):
        filePath = 'E:/Mirai/mirai/img/setu/'
    elif(msg.find('切噜') != -1):
        filePath = 'E:/Mirai/mirai/img/chieru/'
    elif(msg.find('镜华') != -1):
        filePath = 'E:/Mirai/mirai/img/kyoka/'
    elif(msg.find('露娜') != -1):
        filePath = 'E:/Mirai/mirai/img/luna/'
    elif(msg.find('帕琪') != -1):
        filePath = 'F:/lsl/TouHou/Image/2020-帕秋莉/'
    elif(msg.find('芙兰') != -1):
        filePath = 'F:/lsl/TouHou/Image/2020-芙兰/'
    elif(msg.find('膜') != -1):
        filePath = 'E:/Mirai/mirai/img/mo/'
    elif(msg.find('奥特曼') != -1):
        filePath = 'E:/Mirai/mirai/img/atm/'
    elif(msg.find('爱抖露') != -1):
        filePath = 'F:/アイドル/'
    else:
        return
    for i, j, k in os.walk(filePath):
        file = filePath + k[random.randint(0, len(k) - 1)]
    print(file)
    message = MessageChain.create([
        Image.fromLocalFile(Path(file))
    ])
    await app.sendGroupMessage(group, message)
