import html
import re
import time
from typing import List, Any
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import requests
from urllib.parse import urlparse

header_template = '''---
title: {time} 宅舞部投稿月报
categories:
  - 宅舞
tags:
  - 宅舞部
  - 动漫协会
cover: {cover}
date: {date}
---
# {time} 宅舞部投稿月报
'''

body_template = '''
<div class="monthly-report-container">
</div>
'''

css_template = '''
<style>
  /* 简单的CSS样式，让页面看起来更整洁 */
  body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f4f4f4;
  }
  .monthly-report-container {
    max-width: 1000px;
    margin: auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  }
  h1 {
    text-align: center;
    color: #333;
  }
  .video-item {
    display: flex; /* 启用Flexbox布局 */
    border-bottom: 1px solid #eee;
    padding: 15px 0;
    align-items: center; /* 垂直居中对齐 */
  }
  .video-item:last-child {
    border-bottom: none; /* 最后一个视频项没有下边框 */
  }
  .thumbnail-area {
    flex: 0 0 200px; /* 封面区域固定宽度 */
    margin-right: 20px;
  }
  .thumbnail-area img {
    width: 100%;
    height: auto;
    display: block;
    border-radius: 4px;
  }
  .info-area {
    flex-grow: 1; /* 信息区域占据剩余空间 */
  }
  .info-area a {
    font-size: 1.2em;
    color: #007bff;
    text-decoration: none; /* 移除链接下划线 */
    font-weight: bold;
  }
  .info-area a:hover {
    text-decoration: underline;
  }
  .creator {
    color: #666;
    margin-top: 5px;
    font-style: italic;
  }
  .creator a {
    font-size: 1em;
    font-weight: unset;
    color: #666;
    margin-top: 5px;
    font-style: italic;
  }
  .creator a:hover {
    text-decoration: underline;
  }
  /* --- 针对小屏幕设备的样式优化 (手机端) --- */
  @media (max-width: 724px) {
    /* 整体容器内边距调整 */
    .monthly-report-container {
      padding: 10px;
    }
    /* 1. 让视频项从横向排列变为纵向堆叠 */
    .video-item {
      flex-direction: column;
      align-items: flex-start;
    }
    /* 2. 调整封面区域的宽度，使其占满整行 */
    .thumbnail-area {
      flex: 0 0 100%;
      width: 100%;
      max-width: 100%; /* 在小屏上允许占满 */
      margin-right: 0;
      margin-bottom: 10px; /* 在图片下方增加间距 */
    }
    /* 3. 确保信息区域宽度也是 100% */
    .info-area {
      width: 100%;
    }
    /* 4. 优化标题大小 */
    .info-area a {
      font-size: 1.1em;
    }
  }
</style>'''

User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"

headers = {"User-Agent": User_Agent,
           "Referer": "https://www.bilibili.com/"}


def download_image(url, save_dir='./'):
    """
    下载图片到指定目录，如果文件已存在则跳过

    Args:
        url (str): 图片的URL地址
        save_dir (str or Path): 保存目录
    Returns:
        Path: 保存的文件路径，如果失败则返回None
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    filename = Path(urlparse(url).path).name
    file_path = save_path / filename

    if file_path.exists():
        return file_path

    try:
        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                with open(file_path, 'wb') as f:
                    f.write(response.content)

                return file_path
            except Exception:
                if file_path.exists():
                    file_path.unlink()
                time.sleep(1)
        return None
    except Exception:
        if file_path.exists():
            file_path.unlink()
        return None


class VideoItem:
    """存储视频信息的类"""

    VIDEO_SITE_BASE_URL = 'https://www.bilibili.com'

    def __init__(self, bvid: str, raw_html: str = None):
        """
        初始化VideoItem对象

        参数:
        bvid (str): 视频bv号
        raw_html (str): 原始HTML片段，提供时进入降级模式（不请求API）
        pic (str): 视频封面的图片地址URL
        title (str): 视频标题
        pubdate (int): 发布时间戳
        author (List[Any]): 作者对象数组
        """
        self.bvid = bvid  # 视频bv号
        self.raw_html = raw_html
        if raw_html is not None:
            self.pic = ''
            self.title = ''
            self.pubdate = None
            self.author = []
            self.local_pic = ''
            return
        video_info = self.parse_bv(bvid)
        self.pic = video_info['pic']  # 封面图片URL
        self.title = video_info['title']  # 视频标题
        self.pubdate = video_info['pubdate']  # 发布时间戳
        self.author = video_info['author']  # 作者对象数组
        # 本地图片路径
        dt = datetime.fromtimestamp(video_info['pubdate'])
        file_name = f'odottemita{dt.strftime("%Y-%m")}'
        img_dir = base_dir / 'img' / file_name
        t = download_image(self.pic, img_dir)
        if t is None:
            raise RuntimeError(f"封面下载失败: {self.pic}")
        self.local_pic = f"/{'/'.join(t.parts[-3:])}"

    def __str__(self) -> str:
        """返回对象的字符串表示"""
        pubdate_str = (
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.pubdate))
            if self.pubdate is not None else 'unknown'
        )
        author_count = len(self.author)
        return f"VideoItem(id='{self.bvid}', title='{self.title}', pubdate={pubdate_str}, author_count={author_count})"

    def __repr__(self) -> str:
        """返回对象的官方字符串表示"""
        return f"VideoItem(bvid='{self.bvid}', pic='{self.pic}', title='{self.title}', pubdate={self.pubdate}, author={self.author})"

    # 相等性基于bvid
    def __eq__(self, other: Any) -> bool:
        """检查两个VideoItem是否相等（基于bvid）"""
        if not isinstance(other, VideoItem):
            return NotImplemented
        return self.bvid == other.bvid

    # 排序基于pubdate，如果pubdate相同则基于bvid
    def __lt__(self, other: Any) -> bool:
        """检查当前VideoItem是否早于另一个（基于pubdate，相同则基于bvid）"""
        if not isinstance(other, VideoItem):
            return NotImplemented

        # pubdate缺失的降级条目排到最后
        if self.pubdate is None or other.pubdate is None:
            if self.pubdate is None and other.pubdate is None:
                return False
            return other.pubdate is None

        # 首先比较pubdate
        if self.pubdate != other.pubdate:
            return self.pubdate < other.pubdate

        # 如果pubdate相同，则比较bvid以确保稳定性
        return self.bvid < other.bvid

    # 哈希值基于bvid
    def __hash__(self) -> int:
        """返回对象的哈希值（基于bvid）"""
        return hash(self.bvid)

    def _generate_authors_html(self) -> str:
        """
        生成作者信息的HTML片段

        返回:
        str: 作者信息的HTML字符串

        """
        # 这里暂时留空，根据具体的作者对象结构来实现
        # 下面是一个示例实现，根据不同的作者对象类型生成不同的HTML

        if not self.author:
            return '<span class="no-authors">暂无作者信息</span>'

        authors_html_parts = []

        for author in self.author:
            if author['title'] == '摄影':
                continue
            authors_html_parts.append(
                f'''<a href="https://space.bilibili.com/{author['mid']}">@{author['name']}</a>''')
        return '\n        '.join(authors_html_parts)

    @classmethod
    def parse_bv(cls, bvid):
        url = "https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

        url = url.format(bvid=bvid)

        data = None
        last_exc = None
        for _ in range(3):
            try:
                r = requests.get(url, headers=headers, timeout=10)
                data = r.json()['data']
                if data:
                    break
            except Exception as e:
                last_exc = e
            time.sleep(1)
        if not data:
            raise RuntimeError(f"获取视频信息失败: {bvid}") from last_exc
        # print(data)
        pic = data['pic']
        title = data['title']
        author = [data['owner']]
        pubdate = data['pubdate']
        author[0]['title'] = 'UP主'
        if 'staff' in data:
            author = data['staff']

        return {
            'pic': pic,
            'title': title,
            'pubdate': pubdate,
            'author': author,
        }

    def to_html(self, video_site_base_url: str = 'https://www.bilibili.com') -> str:
        """
        生成视频项的HTML代码

        参数:
        video_site_base_url (str, optional): 视频网站的基础URL

        返回:
        str: 视频项的HTML字符串
        """
        # 降级条目直接使用原有HTML，避免重新生成时丢失信息
        if self.raw_html is not None:
            return self.raw_html

        # 使用指定的基础URL或默认值
        base_url = video_site_base_url or self.VIDEO_SITE_BASE_URL

        # 对文本内容进行HTML转义，防止XSS攻击
        escaped_title = html.escape(self.title)

        # 生成作者信息的HTML
        authors_html = self._generate_authors_html()

        # 构建完整的HTML
        html_template = f'''
  <div class="video-item">
    <div class="thumbnail-area">
      <img src="{self.local_pic}" alt="视频封面" />
    </div>
    <div class="info-area">
      <a href="{base_url}/video/{self.bvid}" target="_blank">
        {escaped_title}
      </a>
      <div class="creator">
        {authors_html}
      </div>
    </div>
  </div>'''
        return html_template

    @classmethod
    def from_html(cls, html_string: str) -> 'VideoItem':
        """
        从HTML字符串创建VideoItem对象

        参数:
        html_string (str): HTML字符串

        返回:
        VideoItem: 创建的VideoItem对象

        异常:
        ValueError: 如果无法从HTML中提取必要的信息
        """
        # 提取视频ID
        bvid_match = re.search(r'href="[^"]*/video/([^"?]+)', html_string)
        if not bvid_match:
            # 尝试其他可能的格式
            bvid_match = re.search(r'data-video-id="([^"]+)"', html_string)

        if not bvid_match:
            raise ValueError("无法从HTML中提取视频ID")

        bvid = bvid_match.group(1)

        try:
            return cls(bvid)
        except Exception as e:
            # API失败时保留原有HTML，避免重建月报时丢失旧条目
            print(f"[警告] 视频信息获取失败，保留原有HTML: {bvid} ({e})")
            return cls(bvid, raw_html=html_string)

    @classmethod
    def batch_from_html(cls, html_list: List[str]) -> List['VideoItem']:
        """
        从多个HTML字符串批量创建VideoItem对象

        参数:
        html_list (List[str]): HTML字符串列表

        返回:
        List[VideoItem]: VideoItem对象列表
        """
        videos = []
        for html_str in html_list:
            try:
                video = cls.from_html(html_str)
                videos.append(video)
            except Exception as e:
                print(f"[警告] 解析HTML失败: {e}")
                continue
        return videos


def get_videos_from_blog(content):
    """
    优雅地提取和修改HTML片段

    Args:
        file_path: 输入文件路径
        output_path: 输出文件路径（如为None则覆盖原文件）
    """
    # 读取文件内容

    # 提取HTML片段
    # 使用非贪婪匹配，匹配整个div（包括嵌套）
    pattern = r'(<div\s+class="monthly-report-container"[^>]*>.*?</div>\s*</div>*)'
    # 注意：上面的正则可能需要根据实际情况调整匹配结束条件

    # 更健壮的匹配方式：匹配从开始到文件结束，然后通过BeautifulSoup处理
    start_pattern = r'<div\s+class="monthly-report-container"[^>]*>'
    start_match = re.search(start_pattern, content, re.IGNORECASE)

    if not start_match:
        return None

    start_pos = start_match.start()

    # 使用栈来找到匹配的结束标签
    stack = []
    pos = start_pos
    in_tag = False
    tag_buffer = ""

    while pos < len(content):
        if content[pos] == '<':
            in_tag = True
            tag_buffer = ""

        if in_tag:
            tag_buffer += content[pos]
            if content[pos] == '>':
                in_tag = False
                tag = tag_buffer.lower()

                # 检查是否是div标签
                if tag.startswith('<div'):
                    # 不是自闭合标签
                    if not tag.endswith('/>'):
                        stack.append('div')
                elif tag.startswith('</div'):
                    if stack:
                        stack.pop()
                        if not stack:  # 找到了匹配的结束标签
                            end_pos = pos + 1
                            break

        pos += 1

    # 提取HTML片段
    html_fragment = content[start_pos:end_pos]
    # 使用BeautifulSoup解析这个片段
    soup = BeautifulSoup(html_fragment, 'html.parser')

    # 找到目标div
    target_div = soup.find('div', class_='monthly-report-container')

    if not target_div:
        print("BeautifulSoup解析后未找到目标div")
        return None
    videos = target_div.find_all('div', class_='video-item')
    vs = VideoItem.batch_from_html([str(i) for i in videos])
    return vs


def add_blog(bvid: str):
    '''
    接受一个视频，将其添加到博客当中
    根据bvid先查找到需要添加的图片文件夹和md文件，该步骤需要解析视频获得时间戳进行
    '''
    # 根据bvid先查找到需要添加的图片文件夹和md文件，该步骤需要解析视频获得时间戳进行
    item = VideoItem(bvid)
    pubdate = item.pubdate

    dt = datetime.fromtimestamp(pubdate)

    # 格式化datetime对象为字符串
    formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    print("日期时间：", formatted_dt)

    file_name = f'odottemita{dt.strftime("%Y-%m")}'
    post_file = base_dir / '_posts' / f'{file_name}.md'
    img_dir = base_dir / 'img' / file_name
    print(post_file)
    print(img_dir)
    post_content = ''
    time_str = dt.strftime("%Y 年 %m 月")
    if post_file.exists():
        # 如果存在，解析文件
        with open(post_file, encoding='utf-8') as f:
            post_content = f.read()
    else:
        # 如果文件不存在，生成新文件（只读取全局模板，不回写，避免跨月污染）
        post_content = f'''{header_template.format(time=time_str, cover=item.local_pic, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}
{body_template}
{css_template}
'''
    vs = get_videos_from_blog(post_content)
    if vs is None:
        raise RuntimeError(f"无法从 {post_file} 解析出月报容器，已中止写入以保护原文件")
    if (item not in vs):
        vs.append(item)
    vs.sort()

    # 与get_videos_from_blog使用同样的宽松正则定位容器，避免口径不一致
    container_match = re.search(
        r'<div\s+class="monthly-report-container"[^>]*>', post_content)
    if not container_match:
        raise RuntimeError(f"未能在 {post_file} 中定位月报容器，已中止写入以保护原文件")
    header = post_content[:container_match.start()]
    if vs[0].local_pic:
        repl = 'cover: ' + vs[0].local_pic
        header = re.sub(r'^cover: .*$', lambda _: repl,
                        header, flags=re.MULTILINE)

    post_content = f'''{header}<div class="monthly-report-container">{"".join([i.to_html() for i in vs])}
</div>
{css_template}
'''
    post_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = post_file.with_name(post_file.name + '.tmp')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(post_content)
    tmp_file.replace(post_file)
    return time_str

    # print(item.to_html('https://www.bilibili.com'))


def reflash_blog():
    import subprocess
    subprocess.run(['hexo', 'g'], cwd='/home/shinoai/blog')

base_dir = Path('/home/shinoai/blog/source')

if __name__ == '__main__':
    bvid = 'BV1Wa2CBVE1B'
    add_blog(bvid)
