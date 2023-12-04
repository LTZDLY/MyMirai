import os
import random
from io import BytesIO
from pathlib import Path

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from PIL import Image as Img
from PIL import ImageDraw, ImageFont

fontpath = "src/static/msyh.ttc"


def text_to_image(text, fontpath="src/static/msyh.ttc", margin = 4):
    if text[-1] == '\n':
        text = text[:-1]
    font = ImageFont.truetype(fontpath, 24)
    padding = 10
    text_list = text.split("\n")
    max_width = 0
    for text in text_list:
        w, h = font.getsize(text)
        max_width = max(max_width, w)
    wa = max_width + padding * 2
    ha = h * len(text_list) + margin * (len(text_list) - 1) + padding * 2
    print(text_list)
    print(wa, ha)
    print(max_width)
    i = Img.new("RGB", (wa, ha), color=(255, 255, 255))
    draw = ImageDraw.Draw(i)
    for j in range(len(text_list)):
        text = text_list[j]
        draw.text(
            (padding, padding + j * (margin + h)), text, font=font, fill=(0, 0, 0)
        )
    return i


def image_to_bytes(img, format="PNG"):
    output_buffer = BytesIO()
    img.save(output_buffer, format)
    return output_buffer.getvalue()


async def seImage(app, group, msg: str):
    message = ""
    filePath = ""
    file = ""
    if msg.find("小蓝") != -1:
        msg = msg.replace("小蓝", "爱抖露")
        # await app.send_group_message(group, MessageChain([Plain("已自动进行转义：小蓝->爱抖露")]))
    elif msg.find("美少女") != -1:
        msg = msg.replace("美少女", "爱抖露")
        # await app.send_group_message(group, MessageChain([Plain("已自动进行转义：美少女->爱抖露")]))
    if msg.find("猫") != -1:
        filePath = "./source/img/cat/"
    elif msg.find("狗") != -1:
        filePath = "./source/img/dog/"
    elif msg.find("色图") != -1:
        filePath = "./source/img/setu/"
    elif msg.find("切噜") != -1:
        filePath = "./source/img/chieru/"
    elif msg.find("镜华") != -1:
        filePath = "./source/img/kyoka/"
    elif msg.find("露娜") != -1:
        filePath = "./source/img/luna/"
    elif msg.find("栞") != -1:
        filePath = "./source/img/shiori/"
    elif msg.find("帕琪") != -1:
        filePath = "F:/lsl/TouHou/Image/2020-帕秋莉/"
    elif msg.find("芙兰") != -1:
        filePath = "F:/lsl/TouHou/Image/2020-芙兰/"
    elif msg.find("膜") != -1:
        filePath = "./source/img/mo/"
    elif msg.find("奥特曼") != -1:
        filePath = "./source/img/atm/"
    elif msg.find("爱抖露") != -1:
        filePath = "./source/img/idol/"
    else:
        return
    for i, j, k in os.walk(filePath):
        file = filePath + k[random.randint(0, len(k) - 1)]
    print(file)
    try:
        message = MessageChain([Image(path=file)])
        await app.send_group_message(group, message)
    except:
        return
