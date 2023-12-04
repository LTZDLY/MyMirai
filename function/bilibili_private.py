from io import BytesIO

import requests
from PIL import Image as Img
from PIL import ImageDraw, ImageFilter, ImageFont

from graia.ariadne.util.async_exec import cpu_bound

TABLE_WIDTH = 4
MASSAGE_WIDTH = 1500
DIALOG_WIDTH = 1000
LINE_CHAR_COUNT = 30 * 2  # 每行字符数：30个中文字符(=60英文字符)
MIN_MASSAGE_HEIGHT = 75
ROW_SPACE = 10
FONTSIZE = 35
VIDEOSIZE = 25
TIMESIZE = 25
HEAD_SIZE = 75
MESSAGE_SPACE = 15
MYFONT = r"./source/font/DengXian.ttf"
NAME_BOARDER_WIDTH = 2


def line_break(line: str, char_count=LINE_CHAR_COUNT) -> str:
    ret = ""
    width = 0
    for c in line:
        if len(c.encode("utf8")) == 3:  # 中文
            if char_count == width + 1:  # 剩余位置不够一个汉字
                width = 2
                ret += "\n" + c
            else:  # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == "\t":
                space_c = TABLE_WIDTH - width % TABLE_WIDTH  # 已有长度对TABLE_WIDTH取余
                ret += " " * space_c
                width += space_c
            elif c == "\n":
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= char_count:
            ret += "\n"
            width = 0
    if ret.endswith("\n"):
        return ret[:-1]
    return ret


def circle_corner(img, radii: int = 30, cor: tuple = (1, 1, 1, 1)):
    """
    为图片添加圆角，cor为长度4的元组，代表从上到下从左到右是否需要添加圆角。
    """
    circle = Img.new("L", (radii * 2, radii * 2), 0)  # 创建黑色方形
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形

    img = img.convert("RGBA")
    w, h = img.size

    # 创建一个alpha层，存放四个圆角，使用透明度切除圆角外的图片
    alpha = Img.new("L", img.size, 255)
    if cor[0]:
        alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    if cor[1]:
        alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    if cor[2]:
        alpha.paste(
            circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii)
        )  # 右下角
    if cor[3]:
        alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见

    # # 添加圆角边框
    # draw = ImageDraw.Draw(img)
    # draw.rounded_rectangle(img.getbbox(), outline="black", width=3, radius=radii)
    return img


def circle(img_path):
    # 圆形头像
    # cir_path = path_name + "/" + cir_file_name

    yzmdata = requests.get(img_path)
    tempIm = BytesIO(yzmdata.content)

    ima = Img.open(tempIm).convert("RGBA").resize((HEAD_SIZE, HEAD_SIZE), Img.LANCZOS)

    circle = Img.new("L", (HEAD_SIZE, HEAD_SIZE), 0)  # 创建黑色方形
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, HEAD_SIZE, HEAD_SIZE), fill=255)  # 黑色方形内切白色圆形

    ima.putalpha(circle)  # 白色区域透明可见，黑色区域不可见

    return ima


def get_font_render_size(text, size):
    """
    通过将给定的文本用给定的字体在很大的画布上渲染来确定字体的大小
    """
    if not text:
        return (0, 0)
    # 获取字体大小
    r = (((len(text)) * size), size)
    canvas = Img.new("RGB", r)
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(MYFONT, size)
    draw.text((0, 0), text, font=monospace, fill=(255, 255, 255))
    # canvas.show()
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    return size


def draw_text(text: str, sender=0):
    # 绘制对话

    if not sender:
        bkrgb = (255, 255, 255)
        ftrgb = (0, 0, 0)
    else:
        bkrgb = (128, 185, 242)
        ftrgb = (255, 255, 255)

    txt = text.split("\n")
    lx = 0
    ly = 0
    for i in txt:
        s = get_font_render_size(i, FONTSIZE)
        lx = max(lx, s[0])
        ly += ROW_SPACE + FONTSIZE

    x = lx + 60
    y = ly + 45
    canvas = Img.new("RGB", (x, y), (bkrgb))
    # s = get_font_render_size(text, fontsize)

    ny = 25
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(MYFONT, FONTSIZE)
    for i in txt:
        draw.text((30, ny), i, font=monospace, fill=ftrgb)
        ny += ROW_SPACE + FONTSIZE

    if not sender:
        return circle_corner(canvas, 30, (0, 1, 1, 1))
    else:
        return circle_corner(canvas, 30, (1, 0, 1, 1))


def draw_video(content):
    bkrgb = (255, 255, 255)
    ftrgb = (0, 0, 0)

    yzmdata = requests.get(content["thumb"])
    tempIm = BytesIO(yzmdata.content)

    vid_img = Img.open(tempIm).convert("RGBA")
    img_txt = line_break(content["title"], 45)

    vid_img = vid_img.resize(
        (864, vid_img.size[1] * 864 // vid_img.size[0]),
        Img.LANCZOS,
    )

    txt = img_txt.split("\n")
    lx = vid_img.size[0] - 62
    ly = 0
    for i in txt:
        s = get_font_render_size(i, FONTSIZE)
        ly += ROW_SPACE + FONTSIZE

    y = ly + 45
    canvas = Img.new("RGB", (lx + 60, ly + 45), bkrgb)

    ny = 22
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(MYFONT, FONTSIZE)
    for i in txt:
        draw.text((30, ny), i, font=monospace, fill=ftrgb)
        ny += ROW_SPACE + FONTSIZE

    # canvas.show()

    img_text = Img.new(
        "RGBA", (canvas.size[0], canvas.size[1] + vid_img.size[1]), (255, 255, 255, 255)
    )
    img_text.paste(vid_img, (0, 0))
    img_text.paste(canvas, (0, vid_img.size[1]))

    text = "投稿视频"
    s = get_font_render_size(text, VIDEOSIZE)
    vid_tag = Img.new("RGBA", (s[0] + 25, s[1] + 15), (255, 103, 154))
    draw = ImageDraw.Draw(vid_tag)
    monospace = ImageFont.truetype(MYFONT, VIDEOSIZE)
    draw.text((12, 6), text, font=monospace, fill=(255, 255, 255))
    vid_tag = circle_corner(vid_tag, 5)

    img_text = circle_corner(img_text, 30)
    a3 = vid_tag.getchannel("A")
    img_text.paste(vid_tag, (705, 30), mask=a3)

    return img_text


def draw_img(content, sender=0):
    yzmdata = requests.get(content["url"])
    tempIm = BytesIO(yzmdata.content)

    img_txt = Img.open(tempIm).convert("RGBA")
    if img_txt.size[0] > DIALOG_WIDTH:
        img_txt = img_txt.resize(
            (DIALOG_WIDTH, img_txt.size[1] * DIALOG_WIDTH // img_txt.size[0]),
            Img.LANCZOS,
        )
    elif img_txt.size[1] < MIN_MASSAGE_HEIGHT:
        img_txt = img_txt.resize(
            (
                img_txt.size[0] * MIN_MASSAGE_HEIGHT // img_txt.size[1],
                MIN_MASSAGE_HEIGHT,
            ),
            Img.LANCZOS,
        )

    if not sender:
        return circle_corner(img_txt, 30, (0, 1, 1, 1))
    else:
        return circle_corner(img_txt, 30, (1, 0, 1, 1))


def piece_header(dialog: Img, face, sender, myface):
    """将对话框和头像拼接在一起组成一条消息"""
    a2 = dialog.getchannel("A")
    oriimg = Img.new("RGBA", (dialog.size[0], dialog.size[1]), (168, 226, 250))
    oriimg.putalpha(a2)

    newimg = Img.new(
        "RGBA", (dialog.size[0] + 20, dialog.size[1] + 20), (244, 245, 247, 255)
    )
    a = dialog.getchannel("A")
    newimg.paste(oriimg, (10, 10), a)

    gaussImage = newimg.filter(ImageFilter.GaussianBlur(5))
    gaussImage.paste(dialog, (10, 5), a2)
    a2 = gaussImage.getchannel("A")

    img = Img.new("RGBA", (MASSAGE_WIDTH, dialog.size[1] + 30), (244, 245, 247, 255))
    if not sender:
        img_head = face
    else:
        img_head = myface

    a1 = img_head.getchannel("A")
    a2 = gaussImage.getchannel("A")

    if not sender:
        img.paste(
            gaussImage,
            box=(MESSAGE_SPACE * 2 + HEAD_SIZE - 10, MESSAGE_SPACE - 5),
            mask=a2,
        )
        img.paste(img_head, box=(MESSAGE_SPACE, MESSAGE_SPACE), mask=a1)
    else:
        img.paste(
            gaussImage,
            box=(
                MASSAGE_WIDTH
                - (dialog.size[0] + MESSAGE_SPACE * 3 + HEAD_SIZE)
                + MESSAGE_SPACE
                - 10,
                MESSAGE_SPACE - 5,
            ),
            mask=a2,
        )
        img.paste(
            img_head,
            box=(MASSAGE_WIDTH - MESSAGE_SPACE - HEAD_SIZE, MESSAGE_SPACE),
            mask=a1,
        )

    return img


@cpu_bound
def draw_messages(msg_list):
    img_list = []

    for i in msg_list:
        name = i["name"]
        face = circle(i["face"])
        myface = circle(i["myface"])
        msgs = i["msgs"]
        msgs_img = []
        y = 0
        x = MASSAGE_WIDTH
        for j in msgs:
            sender = 1 if "sender" in j else 0
            if j["type"] == "video":
                img_temp = draw_video(j["content"])
            elif j["type"] != "img":
                img_temp = draw_text(line_break(j["content"]["content"]), sender)
            else:
                img_temp = draw_img(j["content"], sender)

            img_temp = piece_header(img_temp, face, sender, myface)
            msgs_img.append(img_temp)
            y += img_temp.size[1]

        img = Img.new(
            "RGBA", (x, y + 90 + (60 + TIMESIZE) * len(msgs)), (244, 245, 247, 255)
        )

        # 绘制姓名框
        a = ImageDraw.ImageDraw(img)
        a.rectangle(
            ((0, 0), (x, HEAD_SIZE)),
            fill=(255, 255, 255),
            outline=(233, 234, 236),
            width=NAME_BOARDER_WIDTH,
        )

        # 绘制姓名
        s = get_font_render_size(name, FONTSIZE)
        s_y = (HEAD_SIZE - s[1]) // 2
        s_x = (x - s[0]) // 2
        title = ImageDraw.Draw(img)
        monospace = ImageFont.truetype(MYFONT, FONTSIZE)
        title.text((s_x, s_y), name, font=monospace, fill=(0, 0, 0))

        ny = 90  # 下一行开始绘制的y坐标
        for j in range(len(msgs_img) - 1, -1, -1):
            # 逆序遍历，图片从上往下绘制，保证旧的消息在上方
            # 绘制时间
            ny += 20
            time = msgs[j]["time"]
            t = get_font_render_size(time, TIMESIZE)
            # print(t)
            s_x = (x - t[0]) // 2
            monospace2 = ImageFont.truetype(MYFONT, TIMESIZE)
            title.text((s_x, ny), time, font=monospace2, fill=(153, 153, 153))
            ny += t[1] + 40

            # 粘贴消息图片
            img.paste(msgs_img[j], (0, ny))
            ny += msgs_img[j].size[1]

        img_list.append(img.resize((img.size[0] // 2, img.size[1] // 2), Img.LANCZOS))
    return img_list
