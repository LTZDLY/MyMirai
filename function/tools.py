
import base64
from functools import reduce
from hashlib import md5
import json

import requests
import time
import urllib

# ---------------- WBI 签名（参考 function/wbi.md） ----------------


mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]


def getMixinKey(orig: str):
    '对 imgKey 和 subKey 进行字符顺序打乱编码'
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, '')[:32]


def encWbi(params: dict, img_key: str, sub_key: str, curr_time: int = None):
    '为请求参数进行 wbi 签名'
    mixin_key = getMixinKey(img_key + sub_key)
    if curr_time is None:
        curr_time = round(time.time())                                  # 添加 wts 字段
    params['wts'] = curr_time
    params = dict(sorted(params.items()))                               # 按照 key 重排参数
    # 过滤 value 中的 "!'()*" 字符
    params = {
        k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v
        in params.items()
    }
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)  # 序列化参数
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()            # 计算 w_rid
    params['w_rid'] = wbi_sign
    return params


def getWbiKeys() -> tuple[str, str]:
    '获取最新的 img_key 和 sub_key'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.bilibili.com/'
    }
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers)
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content['data']['wbi_img']['img_url']
    sub_url: str = json_content['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key


def getWbi(room_id):
    '按 function/wbi.md 的方式为 getDanmuInfo 参数计算签名，返回 (w_rid, wts)'
    img_key, sub_key = getWbiKeys()
    params = {
        'id': room_id,
        'type': 0,
        'web_location': 444.8,
    }
    signed = encWbi(params, img_key, sub_key)
    return signed['w_rid'], signed['wts']

# ---------------- 无 schema 的 protobuf 通用解码 ----------------

def _read_varint(b: bytes, i: int):
    '从 b 的位置 i 读取一个 varint，返回 (值, 新位置)'
    result = 0
    shift = 0
    while True:
        if i >= len(b):
            raise ValueError('varint 越界')
        byte = b[i]
        i += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, i
        shift += 7


def _parse_protobuf(b: bytes) -> dict:
    '按 protobuf wire format 递归解析字节为 {field_N: 值} 字典，无需 .proto 定义'
    result = {}

    def put(fn, val):
        key = f'field_{fn}'
        if key in result:
            if not isinstance(result[key], list):
                result[key] = [result[key]]
            result[key].append(val)
        else:
            result[key] = val

    i = 0
    while i < len(b):
        tag, i = _read_varint(b, i)
        fn, wt = tag >> 3, tag & 7
        if fn < 1:
            raise ValueError(f'非法字段号 {fn}')
        if wt == 0:
            val, i = _read_varint(b, i)
            put(fn, val)
        elif wt == 1:
            if i + 8 > len(b):
                raise ValueError('fixed64 越界')
            put(fn, int.from_bytes(b[i:i + 8], 'little'))
            i += 8
        elif wt == 2:
            ln, i = _read_varint(b, i)
            if i + ln > len(b):
                raise ValueError('length-delimited 越界')
            put(fn, _decode_chunk(b[i:i + ln]))
            i += ln
        elif wt == 5:
            if i + 4 > len(b):
                raise ValueError('fixed32 越界')
            put(fn, int.from_bytes(b[i:i + 4], 'little'))
            i += 4
        else:
            raise ValueError(f'未知 wire type {wt}')
    return result


def _decode_chunk(chunk: bytes):
    '判定 length-delimited 内容：可打印字符串 / 嵌套消息 / 十六进制回退'
    try:
        s = chunk.decode('utf-8')
        if all(c.isprintable() for c in s):
            return s
    except UnicodeDecodeError:
        pass
    try:
        return _parse_protobuf(chunk)
    except ValueError:
        return chunk.hex()


def decode_protobuf(encoded: str) -> dict:
    """把 base64 字符串解码回 protobuf 消息（无 schema，按 wire format 通用解析）。"""
    # 补齐 base64 padding（防止末尾 '=' 被去掉导致 binascii.Error）
    encoded += "=" * (-len(encoded) % 4)
    raw_bytes = base64.b64decode(encoded)
    return _parse_protobuf(raw_bytes)


# 心跳包为不携带数据的数据包，仅包含数据包头部信息，具体代表如后文所示。其中，心跳包的操作码为2
hb = "00000010001000010000000200000001"


def get_data(room_id):
    Localpath = "./data/cookies.json"
    data = {}
    with open(Localpath, encoding="utf-8") as fr:
        data = json.load(fr)
        fr.close()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
        "cookie": data["pentamei"]["cookie"],
    }
    s = requests.session()
    url = "https://data.bilibili.com/v/"
    rid, wts = getWbi(room_id)
    r = s.get(url, headers=headers)

    """生成握手包数据"""
    # 获取token
    url = (
        "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id=%s&type=0&web_location=444.8&w_rid=%s&wts=%s"
        % (room_id, rid, wts)
    )
    key = ''
    remote = ''
    r = s.get(url, headers=headers)
    if r.json()["code"] == 0:
        key = r.json()["data"]["token"]
        url = r.json()['data']['host_list'][0]
        remote = f"wss://{url['host']}:{url['wss_port']}/sub"

    # 握手包数据内容
    data_json = {
        "uid": data["pentamei"]["uid"],
        "roomid": int(room_id),
        "protover": 3,
        "platform": "web",
        "type": 2,
        "key": key,
    }
    text = json.dumps(data_json)

    # 握手包数据头
    # 数据头长度为16，[1:4]为数据包长度，[5:6]为数据包头部长度，固定为16，[7:8]为协议版本，目前为1，
    # [9:12]为操作码，握手包为7代表认证并加入房间，[13:16]为sequence，可以取常数1

    # 对应为 长度[\x00\x00\x01\x02] 头部长度[\x00\x10] 协议版本[\x00\x01] 操作码[\x00\x00\x00\x07] sequence[\x00\x00\x00\x01]
    size = len(text) + 16  # 十进制下的数据包总长度
    bytesize = hex(size)[2:]  # 十六进制下的数据包总长度
    data_head = (
        "0" * (8 - len(bytesize)) + bytesize + "001000010000000700000001"
    )  # 对长度补0并且将除了长度之后的内容进行拼接

    data_text = text.encode("ascii")  # 将数据包内容转为bytes型
    data = data_head + data_text.hex()  # 将数据包头和数据包内容进行拼接之后返回
    return remote, bytes.fromhex(data)

