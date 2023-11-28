import requests
import json
import asyncio
from aiohttp import ClientSession

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain

compiler_url = "https://wandbox.org/api/compile.ndjson"
compiler_lang = {
    "cpp": "gcc-13.2.0",
    "c++": "gcc-13.2.0",
    "c": "gcc-13.2.0-c",
    "c#": "mono-6.12.0.122",
    "erlang": "erlang-23.3.1",
    "go": "go-1.16.3",
    "groovy": "groovy-3.0.8",
    "java": "openjdk-jdk-15.0.3+2",
    "javascript": "nodejs-16.14.0",
    "js": "nodejs-16.14.0",
    "julia": "julia-1.6.1",
    "lua": "lua-5.4.3",
    "php": "php-8.2.1",
    "pascal": "fpc-3.2.0",
    "python": "cpython-3.10.2",
    "py": "cpython-3.10.2",
    "rust": "rust-1.69.0",
    "ruby": "ruby-3.2.2",
    "sql": "sqlite-3.35.5",
    "swift": "swift-5.3.3",
    "typescript": "typescript-4.2.4",
    "ts": "typescript-4.2.4",
}


async def compiler_main(lang, code):
    com_lang = lang.lower()
    if not com_lang in compiler_lang:
        return f"暂不支持{lang}语言噜~"
    compiler_data = {
        "compiler": compiler_lang[com_lang],
        "code": code,
    }
    async with ClientSession() as session:
        async with session.post(compiler_url, data=json.dumps(compiler_data)) as response:
            res = await response.text()
            return restostring(res, compiler_lang[com_lang])


def restostring(res: str, compiler: str = None) -> str:
    if res.startswith("<!DOCTYPE html>"):
        return "服务器出了点问题，会不会是你的代码导致的呢"
    res = res.replace("\n", "")
    res = res.replace("}{", "},{")
    res = f"[{res}]"
    dd = json.loads(res)
    print(dd)
    s = ""
    if compiler:
        s += f'Compiler: {compiler}\n'
    for i in dd:
        if i["type"] == "Control":
            continue
        elif i["type"] == "StdOut":
            s += f"StdOut:\n{i['data']}\n"
        elif i["type"] == "ExitCode":
            s += f"ExitCode: {i['data']}\n"
        elif i["type"] == "Signal":
            s += f"Signal: {i['data']}\n"
        else:
            s += i["data"]
    return s
