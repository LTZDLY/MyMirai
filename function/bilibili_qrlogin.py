import asyncio
import http.cookiejar as cookielib
import json
import os
from threading import Thread
import time
from binascii import b2a_qp
from io import BytesIO

# import agent
import qrcode
import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from PIL import Image as Img

# from threading import Thread


requests.packages.urllib3.disable_warnings()

User_Agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"

headers = {"User-Agent": User_Agent, "Referer": "https://www.bilibili.com/"}
headerss = {
    "User-Agent": User_Agent,
    "Host": "passport.bilibili.com",
    "Referer": "https://passport.bilibili.com/login",
}


async def bilibili_qrlogin(app, group):
    # 生成二维码并且等待登录
    session = requests.session()

    getlogin = session.get(
        "https://passport.bilibili.com/qrcode/getLoginUrl", headers=headers
    ).json()
    loginurl = requests.get(getlogin["data"]["url"], headers=headers).url
    oauthKey = getlogin["data"]["oauthKey"]
    qr = qrcode.QRCode()
    qr.add_data(loginurl)
    img = qr.make_image()
    img.save(img_bytes := BytesIO(), "png")
    png = img_bytes.getvalue()
    img_bytes.close()
    await app.send_group_message(group, MessageChain([Image(data_bytes=png)]))
    tokenurl = "https://passport.bilibili.com/qrcode/getLoginInfo"

    # 轮询等待
    old_msg = ""
    msg = ""
    f = False
    while 1:
        if old_msg != msg:
            await app.send_group_message(group, MessageChain([Plain(msg)]))
            old_msg = msg
        qrcodedata = session.post(
            tokenurl,
            data={"oauthKey": oauthKey, "gourl": "https://www.bilibili.com/"},
            headers=headerss,
        ).json()
        # msg = (qrcodedata)
        if "-4" in str(qrcodedata["data"]):
            msg = "等待扫码"
        elif "-5" in str(qrcodedata["data"]):
            msg = "已扫码"
        elif "-2" in str(qrcodedata["data"]):
            msg = "二维码过期，登录取消"
            break
        elif "True" in str(qrcodedata["status"]):
            msg = "登录成功，账号："
            f = True
            session.get(qrcodedata["data"]["url"], headers=headers)
            loginurl = session.get(
                "https://api.bilibili.com/x/web-interface/nav",
                verify=False,
                headers=headers,
            ).json()
            if loginurl["code"] == 0:
                name = loginurl["data"]["uname"]
                uid = loginurl["data"]["mid"]
                msg += f"\n{name}（{uid}）"
            break
        else:
            msg = f"其他：{str(qrcodedata)}"
            break
        await asyncio.sleep(2)

    # 登录成功
    await app.send_group_message(group, MessageChain([Plain(msg)]))

    return f, session.cookies


# class showpng(Thread):
#     def __init__(self, data):
#         Thread.__init__(self)
#         self.data = data

#     def run(self):
#         img = Img.open(BytesIO(self.data))
#         img.show()


# def islogin(session):
#     try:
#         session.cookies.load(ignore_discard=True)
#     except Exception:
#         pass
#     loginurl = session.get(
#         "https://api.bilibili.com/x/web-interface/nav", verify=False, headers=headers
#     ).json()
#     if loginurl["code"] == 0:
#         print("Cookies值有效，", loginurl["data"]["uname"], "，已登录！")
#         return session, True
#     else:
#         print("Cookies值已经失效，请重新扫码登录！")
#         return session, False


# def bzlogin():
#     if not os.path.exists("bzcookies.txt"):
#         with open("bzcookies.txt", "w") as f:
#             f.write("")
#     session = requests.session()
#     session.cookies = cookielib.LWPCookieJar(filename="bzcookies.txt")

#     session, status = islogin(session)
#     print(session.cookies)

#     # print(requests.utils.dict_from_cookiejar(session.cookies)["bili_jct"])
#     # print(requests.utils.dict_from_cookiejar(session.cookies)["SESSDATA"])

#     if not status:
#         getlogin = session.get(
#             "https://passport.bilibili.com/qrcode/getLoginUrl", headers=headers
#         ).json()
#         loginurl = requests.get(getlogin["data"]["url"], headers=headers).url
#         oauthKey = getlogin["data"]["oauthKey"]
#         qr = qrcode.QRCode()
#         qr.add_data(loginurl)
#         img = qr.make_image()
#         a = BytesIO()
#         img.save(a, "png")
#         png = a.getvalue()
#         a.close()
#         t = showpng(png)
#         t.start()
#         tokenurl = "https://passport.bilibili.com/qrcode/getLoginInfo"
#         while 1:
#             qrcodedata = session.post(
#                 tokenurl,
#                 data={"oauthKey": oauthKey, "gourl": "https://www.bilibili.com/"},
#                 headers=headerss,
#             ).json()
#             print(qrcodedata)
#             if "-4" in str(qrcodedata["data"]):
#                 print("二维码未失效，请扫码！")
#             elif "-5" in str(qrcodedata["data"]):
#                 print("已扫码，请确认！")
#             elif "-2" in str(qrcodedata["data"]):
#                 print("二维码已失效，请重新运行！")
#             elif "True" in str(qrcodedata["status"]):
#                 print("已确认，登入成功！")
#                 d = session.get(qrcodedata["data"]["url"], headers=headers)
#                 print(d.text)

#                 break
#             else:
#                 print("其他：", qrcodedata)
#             time.sleep(2)
#         session.cookies.save()
#     return session


# if __name__ == "__main__":
#     bzlogin()
