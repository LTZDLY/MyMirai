import asyncio
import datetime

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from function.bilibili import sign
from function.excel import readexcel


async def repeat(app):
    group = [1138925965, 980644912, 372733015, 747861591, 819095234]
    t = datetime.datetime.now()
    h = t.hour
    d = t.day
    m = t.month
    sss = ''
    if (d == 1 and m == 1) or (m == 2 and d == 12):
        if h == 0:
            sss = '切噜~！2021新年快乐！！新的一年也请多多指教哦！~☆'
        elif h == 7:
            sss = '切噜~！已经七点了！2021年的第一天请不要睡懒觉噜！∑'
        elif h == 12:
            sss = '切噜~！中午好！尽情地享受2021年的第一顿午饭吧！☆'
        elif h == 13:
            sss = '一点一点！2021年的第一个一点噜~！∑'
        elif h == 18:
            sss = '切噜~！晚上好！2021年的第一天已经所剩无几了，接下来的时间也请尽情地享受呢噜！☆'
        elif h == 23:
            sss = '切噜~！23点啦！2021年的第一天就这么过去了呢！希望各位接下来的每一天都能过的如此愉快！晚安安！♡'
    else:
        if h == 7:
            asyncio.create_task(sign(app, 372733015))
            asyncio.create_task(readexcel(app, 958056260))
            sss = '切噜~！早上好！已经七点了！该起床并完成每日打卡咯！'
        elif h == 12:
            sss = '切噜~！中午好！12点到啦吃午饭了吗！'
        elif h == 13:
            sss = '一点一点！现在是中午一点切噜~！今天的每日打卡记得做了吗？'
        elif h == 18:
            sss = '切噜~！18点啦！记得吃晚饭哦！'
        elif h == 23:
            asyncio.create_task(sign(app, 372733015))
            sss = '切噜~！23点啦！到睡觉的时候啦！记得最后再检查一次有没有完成打卡！晚安安！'

    if sss != '':
        for i in group:
            await app.sendGroupMessage(i, MessageChain.create([Plain(sss)]))

    group = [1037928476]


async def clock(app):
    while True:
        cur_time = datetime.datetime.now()
        delta = datetime.timedelta(hours=1)
        to_time = datetime.time(cur_time.hour, 0, 0, 0)
        next_time = datetime.datetime.combine(cur_time.date(), to_time) + delta
        sleep_delta = next_time - cur_time
        print(cur_time)
        print(next_time)
        print(sleep_delta.total_seconds())
        await asyncio.sleep(sleep_delta.total_seconds())
        print("时间矫正完成。当前时间：", datetime.datetime.now())
        while True:
            t = datetime.datetime.now()
            if t.minute != 0:
                print("产生分的时间误差，开始矫正", t)
                break
            asyncio.create_task(repeat(app))
            # 这里用 create_task 而不用 await 主要是为了不让 repeat 函数占用时间导致误差
            if t.second != 0:
                print("产生秒的时间误差，开始矫正", t)
                break
            await asyncio.sleep(3600)
            pass

if __name__ == "__main__":
    a = range(5)
    print(a)
    print(sum(a, 2))
