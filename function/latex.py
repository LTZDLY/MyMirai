from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Image, Plain
import requests
from urllib import parse


async def latex(app, group, s: str):
    text = s.replace('latex ', '', 1)
    url = 'https://latex.codecogs.com/png.latex?%5Cdpi%7B300%7D%20%5Cbg_white%20%5Csmall%20'
    text = parse.quote(text)
    text = text.replace('%2B', '&plus;')
    try:
        await app.sendGroupMessage(group, MessageChain.create([Image.fromNetworkAddress(url + text)]))
    except:
        await app.sendGroupMessage(group, MessageChain.create([Plain('输入了无效的公式，请重试')]))
