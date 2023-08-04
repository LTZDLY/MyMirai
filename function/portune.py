# -*- coding: utf-8 -*-

import datetime
from io import BytesIO
import re
import random
import os
'''
import hoshino
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service
from hoshino.util import pic2b64
from hoshino.typing import *
'''
from function.luck_desc import luck_desc
from function.luck_type import luck_type
from PIL import Image as Img, ImageDraw, ImageFont

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain

sv_help = '''
[抽签|人品|运势|抽凯露签]
随机角色/指定凯露预测今日运势
准确率高达114.514%！
'''.strip()
# 帮助文本
# sv = Service('portune', help_=sv_help, bundle='pcr娱乐')

# lmt = DailyNumberLimiter(5)
# 设置每日抽签的次数，默认为1
# Data_Path = hoshino.config.RES_DIR
# 也可以直接填写为res文件夹所在位置，例：absPath = "C:/res/"
Img_Path = './source/imgbase'


# @sv.on_prefix(('抽签', '人品', '运势'), only_to_me=True)
async def portune(app, group: int, member: int, var, model=''):
    '''
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.finish(ev, f'你今天已经抽过签了，欢迎明天再来~', at_sender=True)
    lmt.increase(uid)
    model = 'DEFAULT'

    pic = drawing_pic(model)
    await bot.send(ev, pic, at_sender=True)
    '''

    t = datetime.datetime.now() - datetime.timedelta(hours=0)
    if var[0].date() != t.date():
        # var是一个记录抽到的签的三元组，其中第一项为日期，第二项为图片，第三项为文字
        print("他今天还没抽过运势")
        var[0] = t
        var[1] = ''
        var[2] = {}

    p = Plain('')
    if var[1] and var[2]:
        p = Plain('\n你今天已经抽过签了，这是你今天抽到的签，欢迎明天再来~\n')
    img = drawing_pic(var, model)
    # img.save("./source/bak1.png")
    m = MessageChain(
        [At(member), p, Image(data_bytes=img.getvalue())])
    m.__root__[0].display = ''
    await app.send_group_message(group, m)


'''
@sv.on_fullmatch(('抽臭鼬签', '抽猫猫签', '抽凯露签'))
async def portune_kyaru(bot, ev):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.finish(ev, f'你今天已经抽过签了，欢迎明天再来~', at_sender=True)
    lmt.increase(uid)

    model = 'KYARU'

    pic = drawing_pic(model)
    await bot.send(ev, pic, at_sender=True)
'''


def drawing_pic(var=None, model='') -> BytesIO:
    if not var:
        print("他今天还没抽过运势")
        base_img = ''
        text = {}
    else:
        print("他抽过运势了，用记录的结果")
        base_img = var[1]
        text = var[2]

    fontPath = {
        'title': './source/font/Mamelon.otf',
        'text': './source/font/sakura.ttf'
    }
    if model == 'KYARU':
        base_img = get_base_by_name("frame_1.jpg")
    elif not base_img:
        base_img = random_Basemap()

    filename = os.path.basename(base_img)
    charaid = filename.lstrip('frame_')
    charaid = charaid.rstrip('.jpg')

    img = Img.open(base_img)
    # Draw title
    draw = ImageDraw.Draw(img)

    if not text:
        text, title = luck_get_info(charaid)
    else:
        title = get_luck_type(text)

    if var:
        var[1] = base_img
        var[2] = text

    text = text['content']
    font_size = 45
    color = '#F5F5F5'
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
              title, fill=color, font=ttfront)
    # Text rendering
    font_size = 25
    color = '#323232'
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath['text'], font_size)
    result = decrement(text)
    if not result[0]:
        return Exception('Unknown error in daily luck')
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 +
                (result[0] - 1) * 4 - i * (font_size + 4))
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill=color, font=ttfront)

    # img = pic2b64(img)
    # img = MessageSegment.image(img)
    img.save(img_bytes := BytesIO(), format="PNG")
    img.close()
    return img_bytes


def get_base_by_name(filename) -> str:
    return os.path.join(Img_Path, filename)


def random_Basemap() -> str:
    base_dir = './source/imgbase'
    random_img = random.choice(os.listdir(base_dir))
    return os.path.join(Img_Path, random_img)


def luck_get_info(charaid):
    for i in luck_desc:
        if charaid in i['charaid']:
            typewords = i['type']
            desc = random.choice(typewords)
            # while desc['good-luck'] < 7:
            #     desc = random.choice(typewords)
            return desc, get_luck_type(desc)
    raise Exception('luck description not found')


def get_luck_type(desc):
    target_luck_type = desc['good-luck']
    for i in luck_type:
        if i['good-luck'] == target_luck_type:
            return i['name']
    raise Exception('luck type not found')


def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = ' '
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [numberOfSlices, text[:int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [numberOfSlices, text[:int((length + 1) / 2)] + fillIn,
                    fillIn + space + text[int((length + 1) / 2):]]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality:(i + 1) * cardinality])
    return result


def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)


if __name__ == "__main__":
    drawing_pic()
