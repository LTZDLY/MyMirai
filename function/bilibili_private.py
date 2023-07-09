import os
from io import BytesIO

import requests
from PIL import Image as Img, ImageDraw, ImageFont

fontsize = 70
timesize = 50
myfont = "simhei.ttf"


def circle(img_path):
    # 圆形头像
    path_name = os.path.dirname(img_path)
    cir_file_name = 'cir_img.jpg'
    cir_path = path_name + '/' + cir_file_name

    yzmdata = requests.get(img_path)
    tempIm = BytesIO(yzmdata.content)

    ima = Img.open(tempIm).convert("RGBA")
    size = ima.size
    # ima=ima.resize((size[0] * 2, size[1] * 2), Img.ANTIALIAS)
    size = ima.size
    print(size)
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        ima = ima.resize((r2, r2), Img.ANTIALIAS)
    # 最后生成圆的半径
    r3 = int(r2/2)
    imb = Img.new('RGBA', (r3*2, r3*2), (255, 255, 255, 0))
    pima = ima.load()  # 像素的访问对象
    pimb = imb.load()
    r = float(r2/2)  # 圆心横坐标

    for i in range(r2):
        for j in range(r2):
            lx = abs(i-r)  # 到圆心距离的横坐标
            ly = abs(j-r)  # 到圆心距离的纵坐标
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径
            if l < r3:
                pimb[i-(r-r3), j-(r-r3)] = pima[i, j]

    # imb=imb.resize((size[0] // 2, size[1] // 2), Img.ANTIALIAS)
    # imb.save('E:/Mirai/Graia/cir_img.png')
    return imb


def get_font_render_size(text, size):
    # 获取字体大小
    canvas = Img.new('RGB', (20480, 2048))
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(myfont, size)
    draw.text((0, 0), text, font=monospace, fill=(255, 255, 255))
    # canvas.show()
    bbox = canvas.getbbox()
    # 宽高
    size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    return size


def draw_dialog(text):
    # 绘制对话框
    lb = Img.open('./source/leftbottom.png').convert("RGBA")
    rt = lb.transpose(Img.ROTATE_180)
    rb = lb.transpose(Img.FLIP_LEFT_RIGHT)

    s = get_font_render_size(text, fontsize)
    x = s[0] + 120 + 5
    y = s[1] + 90

    canvas = Img.new('RGB', (s[0] + 20, s[1] + 10), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(myfont, fontsize)
    draw.text((0, 0), text, font=monospace, fill=(0, 0, 0))

    img = Img.new('RGBA', (x, y), (255, 255, 255, 255))
    # print(canvas.size)

    img.paste(lb, (0, y - 60))
    img.paste(canvas, (50, 45))
    img.paste(rt, (65 + s[0], 0))
    img.paste(rb, (65 + s[0], y - 60))
    # print(img.size)
    # img.save('E:/Mirai/Graia/testtt.png')
    return img


def draw_message(text, face):
    # 绘制一条消息
    img_txt = draw_dialog(text)
    img_head = face
    size_txt = img_txt.size
    img_head = img_head.resize((150, 150), Img.ANTIALIAS)

    _, _, _, a1 = img_head.split()
    _, _, _, a2 = img_txt.split()

    img = Img.new(
        "RGBA", (size_txt[0] + 240, size_txt[1] + 60), (244, 245, 247, 255))

    img.paste(img_head, box=(30, 30), mask=a1)
    img.paste(img_txt, box=(210, 30), mask=a2)

    # img.save('E:/Mirai/Graia/testtt.png')
    return img

def draw_img(content, face):

    yzmdata = requests.get(content['url'])
    tempIm = BytesIO(yzmdata.content)

    img_txt = Img.open(tempIm).convert("RGBA")
    
    img_head = face
    size_txt = img_txt.size
    img_head = img_head.resize((150, 150), Img.ANTIALIAS)

    _, _, _, a1 = img_head.split()
    _, _, _, a2 = img_txt.split()

    img = Img.new(
        "RGBA", (size_txt[0] + 240, size_txt[1] + 60), (244, 245, 247, 255))

    img.paste(img_head, box=(30, 30), mask=a1)
    img.paste(img_txt, box=(210, 30), mask=a2)

    # img.save('E:/Mirai/Graia/testtt.png')
    return img

def draw_messages(msg_list):
    img_list = []

    for i in msg_list:
        name = i['name']
        face = circle(i['face'])
        msgs = i['msgs']
        msgs_img = []
        y = 0
        x = 2000
        for j in msgs:
            if j['type'] != 'img':
                img_temp = draw_message(j['content']['content'], face)
                msgs_img.append(img_temp)
                x = max(x, img_temp.size[0])
                y += img_temp.size[1]
            else:
                img_temp = draw_img(j['content'], face)
                msgs_img.append(img_temp)
                x = max(x, img_temp.size[0])
                y += img_temp.size[1]
        img = Img.new('RGBA', (x, y + 200 + 116 * len(msgs)),
                        (244, 245, 247, 255))
        a = ImageDraw.ImageDraw(img)
        a.rectangle(((0, 0), (x, 150)), fill=(255, 255, 255),
                    outline=(233, 234, 236), width=5)

        s = get_font_render_size(name, fontsize)
        s_y = (150 - s[1]) // 2
        s_x = (x - s[0]) // 2

        title = ImageDraw.Draw(img)
        monospace = ImageFont.truetype(myfont, fontsize)
        title.text((s_x, s_y), name, font=monospace, fill=(0, 0, 0))

        ny = 180
        for j in range(len(msgs_img) - 1, -1, -1):
            time = msgs[j]['time']
            t = get_font_render_size(time, timesize)
            # print(t)
            s_x = (x - t[0]) // 2

            monospace2 = ImageFont.truetype(myfont, timesize)
            title.text((s_x, ny + 50), time,
                       font=monospace2, fill=(153, 153, 153))
            ny += t[1] + 80

            img.paste(msgs_img[j], (0, ny))
            ny += msgs_img[j].size[1]

        img_list.append(img)
    return img_list
