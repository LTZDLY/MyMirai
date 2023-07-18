from io import BytesIO
from PIL import Image as Img, ImageDraw, ImageFont

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image


async def ouen(app, txt: str, group):
    add = "simhei.ttf"
    img = Img.open('./source/4.png')
    # 控制表情的叠加位置
    draw = ImageDraw.Draw(img)

    mask = img
    s_background = Img.new(
        "RGBA", (650, 650), (255, 255, 255, 0))  # alpha通道设为0，保证透明度
    s_draw = ImageDraw.Draw(s_background)

    size_max = int(320/len(txt)*2) + 1
    size_min = int(320/len(txt)) - 1

    # print(len(txt))
    if len(txt) == 1:
        font = ImageFont.truetype(add, 180)
        text_size = draw.textsize(txt, font=font)
        # print(text_size)
        if abs(text_size[0] - 180) < 30:
            x, y = 180, 30
        else:
            x, y = 225, 30
    elif len(txt) == 2:
        font = ImageFont.truetype(add, 140)
        text_size = draw.textsize(txt, font=font)
        # print(text_size)
        if abs(text_size[0] - 280) < 20:
            x, y = 130, 50
        elif abs(text_size[0] - 210) < 20:
            x, y = 165, 50
        else:
            x, y = 200, 50
    else:
        x = 110
        for size in range(size_max, size_min, -1):

            font = ImageFont.truetype(add, size)
            text_size = draw.textsize(txt, font=font)
            # print(text_size)
            if text_size[0] > 320:
                continue
            else:
                break

        s = text_size[1]
        y = -0.0009077705156136529 * \
            (pow(s, 2))-0.25326797385620914*s+105.27777777777777
        # print(y)

    s_draw.text((x, y), txt, fill=(0, 0, 0), font=font)
    s_rotate = s_background.rotate(-5, expand=1)  # 图像会转动随机的角度
    mask.resize(s_rotate.size)

    out1 = Img.composite(s_rotate, mask, s_rotate)  # 第一次复合生成的图片是旋转后去黑色背景图片
    mask = out1
    # out1.show()
    img_bytes = BytesIO()
    out1.save(img_bytes, format="PNG")
    out1.close()

    await app.send_group_message(group, MessageChain([
        Image(data_bytes=img_bytes.getvalue())
    ]))
    img_bytes.close()
