from asyncio import sleep
import traceback
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain

from io import BytesIO

import matplotlib.font_manager as mfm
import numpy as np
from matplotlib import mathtext
from PIL import Image as Img

async def draw_latex(t):
    text = f'${t}$'
    color = (0, 0, 0)  # 要使用的颜色
    bfo = BytesIO()  # 创建二进制的类文件对象
    prop = mfm.FontProperties(math_fontfamily='cm', size=64, weight='light')
    mathtext.math_to_image(text, bfo, prop=prop, dpi=72)

    im = Img.open(bfo)  # 打开二进制的类文件对象，返回一个PIL图像对象
    r, g, b, a = im.split()  # 分离出RGBA四个通道
    r, g, b = 255-np.array(r), 255-np.array(g), 255-np.array(b)  # RGB通道反白
    a = r/3 + g/3 + b/3  # 生成新的alpha通道
    r, g, b = r*color[0], g*color[1], b*color[2]  # RGB通道设置为目标颜色
    im = np.dstack((r, g, b, a)).astype(np.uint8)  # RGBA四个通道合并为三维的numpy数组
    im = Img.fromarray(im)  # numpy数组转PIL图像对象
    img_bytes = BytesIO()
    im.save(img_bytes, format="PNG")
    im.close()
    return img_bytes
    # im.save(r'd:\demo_5.png')  # PIL图像对象保存为文件


# def dove() -> str:
#     url = 'http://www.koboldgame.com/gezi/api.php'
#     return requests.get(url).text.split('\"')[1]


async def latex(app, group, s: str):
    text = s.replace('latex ', '', 1)
    try:
        img = await draw_latex(text)
        await app.send_group_message(group, MessageChain([Image(data_bytes=img.getvalue())]))
    except ValueError as e:
        # print (e.args)
        traceback.print_exc()
        await app.send_group_message(group, MessageChain([Plain(e.args[0])]))
    except Exception as e:
        traceback.print_exc()
        await app.send_group_message(group, MessageChain([Plain(traceback.format_exc())]))

# draw_latex("abc+123")