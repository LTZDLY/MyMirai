import emoji
from PIL import Image as Img, ImageDraw, ImageFont
from pilmoji import Pilmoji
from pilmoji.source import HTTPBasedSource, MicrosoftEmojiSource, TwemojiEmojiSource

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image

OUTPUT_PATH = "./source/ouen.png"


class _ResilientEmojiSource(HTTPBasedSource):
    """emoji 图源：优先微软风格，请求失败（含网络异常）时回退 Twitter 风格，均失败返回 None"""

    def __init__(self):
        super().__init__()
        self._fallbacks = (MicrosoftEmojiSource(), TwemojiEmojiSource())

    def get_emoji(self, emoji_char: str, /):
        for source in self._fallbacks:
            try:
                stream = source.get_emoji(emoji_char)
            except Exception:
                continue
            if not stream:
                continue
            try:
                # 验证 CDN 返回的确实是图片（elk.sh 偶尔返回 200 + 非图片内容）
                with Img.open(stream) as probe:
                    probe.load()
                stream.seek(0)
                return stream
            except Exception:
                continue
        return None

    def get_discord_emoji(self, id: int, /):
        return None


def _split_emoji(txt: str):
    """切分文本为 [(是否emoji, 片段)]，emoji 序列（ZWJ组合/肤色修饰符等）整体为一段"""
    segments = []
    last = 0
    for item in emoji.emoji_list(txt):
        start, end = item["match_start"], item["match_end"]
        if start > last:
            segments.append((False, txt[last:start]))
        segments.append((True, txt[start:end]))
        last = end
    if last < len(txt):
        segments.append((False, txt[last:]))
    return segments


def _text_size(draw, text, font):
    """兼容新旧 Pillow 的文本尺寸测量（textsize 在 Pillow 10+ 被移除）"""
    if hasattr(draw, "textsize"):
        return draw.textsize(text, font=font)
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def _visual_len(segments) -> int:
    """视觉字符数：一个 emoji 序列按 1 个字计"""
    return sum(1 if is_e else len(chunk) for is_e, chunk in segments)


def _display_size(draw, font, segments):
    """估算渲染尺寸：文本段按字体测量，emoji 段按字号宽度计（与 pilmoji 的渲染占位一致）"""
    width = 0
    text_only = ""
    for is_e, chunk in segments:
        if is_e:
            width += font.size
        else:
            text_only += chunk
            width += _text_size(draw, chunk, font)[0]
    height = _text_size(draw, text_only, font)[1] if text_only else font.size
    return width, height


def draw_ouen(txt: str) -> str:
    """根据文本绘制应援图并保存到本地，返回图片路径"""
    if not txt:
        raise ValueError("txt 不能为空")
    MYFONT = r"./source/font/simhei.ttf"
    img = Img.open("./source/4.png")
    # 控制表情的叠加位置
    draw = ImageDraw.Draw(img)

    segments = _split_emoji(txt)
    vlen = _visual_len(segments)

    mask = img
    s_background = Img.new("RGBA", (650, 650), (255, 255, 255, 0))  # alpha通道设为0，保证透明度
    with Pilmoji(s_background, source=_ResilientEmojiSource()) as pilmoji:
        size_min = max(int(320 / vlen) - 1, 1)
        size_max = max(int(320 / vlen * 2) + 1, size_min + 1)

        # print(vlen)
        if vlen == 1:
            font = ImageFont.truetype(MYFONT, 180)
            text_size = _display_size(draw, font, segments)
            # print(text_size)
            if abs(text_size[0] - 180) < 30:
                x, y = 180, 30
            else:
                x, y = 225, 30
        elif vlen == 2:
            font = ImageFont.truetype(MYFONT, 140)
            text_size = _display_size(draw, font, segments)
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
                font = ImageFont.truetype(MYFONT, size)
                text_size = _display_size(draw, font, segments)
                # print(text_size)
                if text_size[0] > 320:
                    continue
                else:
                    break

            s = text_size[1]
            y = (
                -0.0009077705156136529 * (pow(s, 2))
                - 0.25326797385620914 * s
                + 105.27777777777777
            )
            # print(y)
        x = int(x)
        y = int(y)
        pilmoji.text((x, y), txt, fill=(0, 0, 0), font=font)
    s_rotate = s_background.rotate(-5, expand=1)  # 图像会转动随机的角度
    mask.resize(s_rotate.size, Img.LANCZOS)

    out1 = Img.composite(s_rotate, mask, s_rotate)  # 第一次复合生成的图片是旋转后去黑色背景图片
    mask = out1
    # out1.show()
    out1.save(OUTPUT_PATH, format="PNG")
    out1.close()
    return OUTPUT_PATH


async def ouen(app, txt: str, group):
    """绘制应援图并通过框架发送图片消息"""
    path = draw_ouen(txt)
    await app.send_group_message(
        group, MessageChain([Image(path=path)])
    )
