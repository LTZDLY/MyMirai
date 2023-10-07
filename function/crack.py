import base64
import json
import math

import cv2
import numpy as np
import requests
from Crypto.Cipher import AES
from PIL import Image as Img, ImageDraw, ImageFont
import glob
import pathlib

from gmssl import sm2
from base64 import b64encode, b64decode

MYFONT = r"./source/font/STZHONGS.ttf"

def sm_2encrypt(info, key):
    sm2_crypt = sm2.CryptSM2(public_key=key, private_key=None)
    encode_info = sm2_crypt.encrypt(info.encode(encoding="utf-8"))
    encode_info = b64encode(encode_info).decode()  # 将二进制bytes通过base64编码
    return encode_info


def check(s: requests.Session, data, point):
    enc = encrypt(json.dumps(point).replace(" ", ""), data["secretKey"])
    resp = s.post(
        "https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0&sid=0/checkCaptcha=1",
        json={
            "token": data["token"],
            "pointJson": enc,
        },
    )
    return resp.json()


def encrypt(s, key):
    def pad(m):
        left = 16 - len(m) % 16
        return m + chr(left) * left

    cipher = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    enc_byte = cipher.encrypt(pad(s).encode("utf-8"))
    return base64.b64encode(enc_byte).decode("ascii")


# 感知哈希算法(pHash)
def pHash(gray, shape=(10, 10)):
    # 缩放32*32
    gray = cv2.resize(gray, (32, 32))  # , interpolation=cv2.INTER_CUBIC

    # # 转换为灰度图
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:10, 0:10]

    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash


# Hash值对比
def cmpHash(hash1, hash2, shape=(10, 10)):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 相等则n计数+1，n最终为相似度
        if hash1[i] == hash2[i]:
            n = n + 1
    return n / (shape[0] * shape[1])


def get_file(file_path, pattern="*") -> list[pathlib.Path]:
    """
    函数 获取给定目录下的所有文件的绝对路径
    参数 file_path: 文件目录
    参数 pattern:默认返回所有文件，也可以自定义返回文件类型，例如：pattern="*.py"
    返回值 abspath:文件路径列表
    """
    all_file = []
    files = pathlib.Path(file_path).rglob(pattern)
    for file in files:
        if pathlib.Path.is_file(file):
            all_file.append(file)
    return all_file


def genImgList(img_paths: list[pathlib.Path]):
    temp = []
    for i in img_paths:
        image = cv2.imread(str(i), cv2.IMREAD_COLOR)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        temp.append({"img": image, "img_gray": image_gray})
    return temp


def selectImg(imglist, img):
    for item in imglist:
        if comp(img, item):
            return item


def rotate(image, angle, center=None, scale=1.0, target=80):
    (w, h) = image.shape[0:2]
    if center is None:
        center = (w // 2, h // 2)
    wrapMat = cv2.getRotationMatrix2D(center, angle, scale)
    top = bottom = (target - w) // 2
    left = right = (target - h) // 2
    while (top + bottom + w) < target:
        top += 1
    while (left + right + h) < target:
        left += 1
    a = cv2.warpAffine(image, wrapMat, (h, w))
    b = cv2.copyMakeBorder(a, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)
    print(b.shape)
    return b


# 使用矩形框
def getCorrect(threImg):
    # 获得有文本区域的点集,求点集的最小外接矩形框，并返回旋转角度
    coords = np.column_stack(np.where(threImg > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(angle + 90)
    else:
        angle = -angle

    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90

    # 仿射变换，将原图校正
    threImg = rotate(threImg, angle)
    return threImg


def preprocess(binary, arg1=1, arg2=2):
    # 3. 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (arg1, arg1))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (arg2, arg2))

    # 4. 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations=1)

    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    erosion = cv2.erode(dilation, element1, iterations=1)

    # 6. 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations=3)

    # 7. 存储中间图片
    cv2.imwrite("binary.png", binary)
    cv2.imwrite("dilation.png", dilation)
    cv2.imwrite("erosion.png", erosion)
    cv2.imwrite("dilation2.png", dilation2)

    return dilation2


def findTextRegion(img):
    region = []

    # 1. 查找轮廓
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 2. 筛选那些面积小的
    for i in range(len(contours)):
        cnt = contours[i]
        # 计算该轮廓的面积
        area = cv2.contourArea(cnt)

        # 面积小的都筛选掉
        # print(area)
        if area < 100:
            continue

        # 轮廓近似，作用很小
        epsilon = 0.001 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # 找到最小的矩形，该矩形可能有方向
        rect = cv2.minAreaRect(cnt)
        # print("rect is: ")
        # print(rect)

        # box是四个点的坐标
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])

        # 筛选那些太细的矩形，留下扁的
        if height > width * 1.2:
            continue

        region.append((box, rect[-1]))

    region.sort(key=lambda i: i[0][0][0])
    return region


def getBinary(img1, img2) -> cv2.typing.MatLike:
    img = cv2.bitwise_xor(img1["img_gray"], img2["img_gray"])
    ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)
    return img


def getData(s: requests.Session):
    resp = s.post(
        "https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0&sid=0/getCaptcha=1"
    )
    return resp.json()["repData"]


def getImageFromBase64(b64):
    buffer = base64.b64decode(b64)
    nparr = np.frombuffer(buffer, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # path_file_num = glob.glob(r'./test/canvas/*.png')
    # cv2.imwrite(f'./test/canvas/{len(path_file_num)}.png', image)
    return image


def init_img(image):
    temp = {}
    image2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    temp["img"] = image
    temp["img_gray"] = image2
    return temp


def comp(img1, img2):
    diffImg1 = cv2.subtract(img1["img_gray"], img2["img_gray"])
    a = cv2.countNonZero(diffImg1)
    print(a)
    if a < 1000:
        return True
    return False


def draw_txt(text, size=25):
    r = (80, 80)
    # r = (((len(text)) * size), size)
    canvas = Img.new("L", r)
    draw = ImageDraw.Draw(canvas)
    monospace = ImageFont.truetype(MYFONT, size)
    draw.text((28, 23), text, font=monospace, fill=(255))
    return np.asarray(canvas)


def crack(data):
    img_b64 = data["originalImageBase64"]
    word_list = data["wordList"]
    buffer = base64.b64decode(img_b64)
    nparr = np.frombuffer(buffer, np.uint8)
    img_target = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    temp = init_img(img_target)

    img_back = selectImg(img_list, temp)
    img_text = getBinary(img_back, temp)
    img_big = preprocess(img_text, 2, 3)

    cdr = []
    region = findTextRegion(img_big)
    # print("r", region)

    if len(region) != 4:
        raise ("error")

    rorate_before = []
    # 4. 用绿线画出这些找到的轮廓
    for mybox in region:
        box = mybox[0]
        d = (box[0] + box[2]) // 2
        x1 = y1 = 999
        x2 = y2 = 0
        for i in box:
            x1 = min(x1, i[0])
            y1 = min(y1, i[1])
            x2 = max(x2, i[0])
            y2 = max(y2, i[1])
        newimg = img_text[y1:y2, x1:x2]
        rorate_before.append(newimg)
        if newimg.shape[0] == 0:
            print(newimg)

        cdr.append(d)
        # cv2.drawContours(temp["img"], [box], 0, (0, 255, 0), 2)
        # cv2.circle(temp["img"], (int(d[0]), int(d[1])), 5, (0, 0, 255), 2)
    # cdr.sort(key=lambda i: i[0])
    print(cdr)
    rorate_after = []
    for item in rorate_before:
        rorate_after.append(getCorrect(item))

    print(word_list)
    word_img = []
    for i in word_list:
        word_img.append(draw_txt(i))

    hashtable = []
    for i in rorate_after:
        hashtable.append(pHash(i))

    wordtable = []
    for i in word_img:
        wordtable.append(pHash(i))

    ans = []
    for i in range(3):
        new = 0
        if cmpHash(wordtable[i], hashtable[i]) > cmpHash(
            wordtable[i], hashtable[i + 1]
        ):
            new = i
        else:
            new = i + 1
        if ans and ans[-1] == new:
            if cmpHash(wordtable[i], hashtable[i]) > cmpHash(
                wordtable[i - 1], hashtable[i]
            ):
                ans[-1] -= 1
                bef = ans[-1]
                for j in range(len(ans) - 2, -1, -1):
                    if ans[j] == bef:
                        ans[j] -= 1
                    bef = ans[j]
                # 回退
                ans.append(i)
            else:
                ans.append(i + 1)
        else:
            ans.append(new)

    print(ans)
    aans = []
    for i in ans:
        temp = {}
        temp["x"] = int(cdr[i][0])
        temp["y"] = int(cdr[i][1])
        aans.append(temp)

    img_new = rorate_after[0].copy()
    img_black = np.zeros((80, 80), np.uint8)
    img_newn = None

    for i in range(1, 4):
        img_new = np.concatenate([img_new, rorate_after[i]], axis=1)

    j = -1
    if 0 in ans:
        img_newn = word_img[0].copy()
        j = 1
    else:
        img_newn = img_black.copy()
        j = 0
    for i in range(1, 4):
        if not i in ans:
            img_newn = np.concatenate([img_newn, img_black], axis=1)
        else:
            img_newn = np.concatenate([img_newn, word_img[j]], axis=1)
            j += 1

    image = np.vstack((img_new, img_newn))
    cv2.imshow(str(123), image)

    # # 带轮廓的图片
    # cv2.imwrite("contours.png", temp["img"])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return aans


l = get_file("./test/canvas/", "*.png")
img_list = genImgList(l)


def crack_main(s: requests.Session):
    for _ in range(20):
        data = getData(s)
        point = crack(data)
        res = check(s, data, point)
        print(res)
        if res["repCode"] == "0000":
            return encrypt(
                data["token"] + "---" + json.dumps(point).replace(" ", ""),
                data["secretKey"],
            )


if __name__ == "__main__":
    s = requests.session()
    print(crack_main(s))
