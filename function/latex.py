from urllib import parse

import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain


def dove() -> str:
    url = 'http://www.koboldgame.com/gezi/api.php'
    return requests.get(url).text.split('\"')[1]


async def latex(app, group, s: str):
    text = s.replace('latex ', '', 1)
    url = 'https://latex.codecogs.com/png.latex?%5Cdpi%7B300%7D%20%5Cbg_white%20%5Csmall%20'
    text = parse.quote(text)
    text = text.replace('%2B', '&plus;')
    try:
        await app.send_group_message(group, MessageChain([Image(url=url + text)]))
    except:
        await app.send_group_message(group, MessageChain([Plain('输入了无效的公式，请重试')]))
