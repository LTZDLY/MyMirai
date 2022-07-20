import os
from pathlib import Path
import random

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain


async def seImage(app, group, msg: str):
    message = ''
    filePath = ''
    file = ''
    if(msg.find('小蓝') != -1):
        msg = msg.replace('小蓝', '爱抖露')
        # await app.send_group_message(group, MessageChain([Plain("已自动进行转义：小蓝->爱抖露")]))
    elif(msg.find('美少女') != -1):
        msg = msg.replace('美少女', '爱抖露')
        # await app.send_group_message(group, MessageChain([Plain("已自动进行转义：美少女->爱抖露")]))
    if(msg.find('猫') != -1):
        filePath = './source/img/cat/'
    elif(msg.find('狗') != -1):
        filePath = './source/img/dog/'
    elif(msg.find('色图') != -1):
        filePath = './source/img/setu/'
    elif(msg.find('切噜') != -1):
        filePath = './source/img/chieru/'
    elif(msg.find('镜华') != -1):
        filePath = './source/img/kyoka/'
    elif(msg.find('露娜') != -1):
        filePath = './source/img/luna/'
    elif(msg.find('栞') != -1):
        filePath = './source/img/shiori/'
    elif(msg.find('帕琪') != -1):
        filePath = 'F:/lsl/TouHou/Image/2020-帕秋莉/'
    elif(msg.find('芙兰') != -1):
        filePath = 'F:/lsl/TouHou/Image/2020-芙兰/'
    elif(msg.find('膜') != -1):
        filePath = './source/img/mo/'
    elif(msg.find('奥特曼') != -1):
        filePath = './source/img/atm/'
    elif(msg.find('爱抖露') != -1):
        filePath = './source/img/idol/'
    else:
        return
    for i, j, k in os.walk(filePath):
        file = filePath + k[random.randint(0, len(k) - 1)]
    print(file)
    try:
        message = MessageChain([
            Image(path=file)
        ])
        await app.send_group_message(group, message)
    except:
        return
