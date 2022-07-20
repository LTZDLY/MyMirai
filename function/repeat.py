import asyncio
import datetime

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain

from function.bilibili import private_msg, sign
from function.data import dancing_group
from function.excel import readexcel


async def repeat(app):
    group = [1138925965, 980644912, 372733015, 747861591, 819095234]
    t = datetime.datetime.now()
    h = t.hour
    d = t.day
    m = t.month
    year = t.year
    sss = ''
    if (d == 1 and m == 1):  # 如果为公历或农历新年
        if h == 0:
            sss = f'切噜~！{year}新年快乐！！新的一年也请多多指教哦！~☆'
        elif h == 7:
            asyncio.create_task(sign(app, 372733015))
            asyncio.create_task(readexcel(app, 958056260))
            sss = f'切噜~！已经七点了！{year}年的第一天请不要睡懒觉噜！∑'
        elif h == 12:
            sss = f'切噜~！中午好！尽情地享受{year}年的第一顿午饭吧！☆'
        elif h == 13:
            sss = f'一点一点！{year}年的第一个一点噜~！∑'
        elif h == 18:
            sss = f'切噜~！晚上好！{year}年的第一天已经所剩无几了，接下来的时间也请尽情地享受呢噜！☆'
        elif h == 23:
            asyncio.create_task(sign(app, 372733015))
            sss = f'切噜~！23点啦！{year}年的第一天就这么过去了呢！希望各位接下来的每一天都能过的如此愉快！晚安安！♡'
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
            await app.send_group_message(i, MessageChain([Plain(sss)]))

    group = [1037928476]


async def getprivate(app, group: int):
    print('正在进行消息拉取...')
    msg = private_msg(app)
    if msg:
        await app.send_group_message(group, msg)
    else:
        print('并没有拉取到东西')


async def reminder(app, group: int, message: MessageChain, d: datetime.timedelta):
    await asyncio.sleep(d.total_seconds())
    await app.send_group_message(group, message.asSendable())


async def remindme(app, group: int, member: int, message: MessageChain):
    message_a = MessageChain([At(member), Plain('\n')])
    message_a.__root__[0].display = ''
    s = message.__root__[1].text
    text = s.split('后提醒我')
    if(len(text) <= 1):
        return
    else:
        rep = text[0]
        t = text[1]
        for i in text[2:]:
            t += '后提醒我' + i
        message.__root__[1].text = t
    day = hour = minute = second = 0
    text = text[0]
    if(text.find('天') != -1):
        text = text.split('天')
        day = text[0]
        text = text[1]
    if(text.find('小时') != -1):
        text = text.split('小时')
        hour = text[0]
        text = text[1]
    if(text.find('分钟') != -1):
        text = text.split('分钟')
        minute = text[0]
        text = text[1]
    elif(text.find('分') != -1):
        text = text.split('分')
        minute = text[0]
        text = text[1]
    if(text.find('秒') != -1):
        text = text.split('秒')
        second = text[0]
        text = text[1]
    try:
        day = abs(float(day))
        hour = abs(float(hour))
        minute = abs(float(minute))
        second = abs(float(second))
        d = datetime.timedelta(days=day, hours=hour,
                               minutes=minute, seconds=second)
    except:
        return
    rep = f'{day}天' if day != 0 else ''
    rep += f'{hour}小时' if hour != 0 else ''
    rep += f'{minute}分' if minute != 0 else ''
    rep += f'{second}秒' if second != 0 else ''
    if rep == '':
        return
    asyncio.create_task(
        reminder(app, group, message_a.extend(message).asSendable(), d))
    message_b = MessageChain([Plain('切噜~♪将在' + rep + '后提醒你：\n')])
    await app.send_group_message(group, message_b.extend(message).asSendable())


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
            asyncio.create_task(getprivate(app, dancing_group))

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
