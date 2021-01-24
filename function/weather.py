import random

import requests
from graia.application.event.messages import GroupMessage
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.broadcast.interrupt.waiter import Waiter

s = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass


async def reporttomorrow(app, group, city, day):
    ss = ''
    if(city[0] == city[1]):
        ss += city[1] + ' ' + city[2]
    else:
        ss += city[0] + ' ' + city[1] + ' ' + city[2]

    url = 'https://wis.qq.com/weather/common?source=pc&weather_type=observe%7Cforecast_1h%7Cforecast_24h%7Cindex%7Calarm%7Climit%7Ctips%7Crise' + \
        '&province=' + city[0] + '&city=' + city[1] + '&county=' + city[2]
    data = s.get(url, headers=headers).json()

    daily = data['data']['forecast_24h'][str(day)]
    ss += '\n' + daily["time"]
    ss += '\n天气: ' + daily['min_degree'] + '°~' + daily['max_degree'] + '°'
    if daily['day_weather'] == daily['night_weather']:
        ss += ' ' + daily['day_weather']
    else:
        ss += ' ' + daily['day_weather'] + \
            '转' + daily['night_weather']
    if daily['day_wind_direction'] == daily['night_wind_direction']:
        ss += ' ' + daily['day_wind_direction']
    else:
        ss += ' ' + daily['day_wind_direction'] + \
            '转' + daily['night_wind_direction']
    if daily['day_wind_power'] == daily['night_wind_power']:
        ss += ' ' + daily['day_wind_power'] + '级'
    else:
        ss += ' ' + daily['day_wind_power'] + \
            '到' + daily['night_wind_power'] + '级'

    ss += '\n数据来源: 腾讯天气'
    await app.sendGroupMessage(group, MessageChain.create([Plain(ss)]))
    pass


async def report(app, group, city):
    ss = ''
    if(city[0] == city[1]):
        ss += city[1] + ' ' + city[2]
    else:
        ss += city[0] + ' ' + city[1] + ' ' + city[2]

    url = 'https://wis.qq.com/weather/common?source=pc&weather_type=observe%7Cforecast_1h%7Cforecast_24h%7Cindex%7Calarm%7Climit%7Ctips%7Crise' + \
        '&province=' + city[0] + '&city=' + city[1] + '&county=' + city[2]
    data = s.get(url, headers=headers).json()

    daily = data['data']['forecast_24h']['1']
    ss += '\n' + daily["time"]
    ss += '\n今日天气: ' + daily['min_degree'] + '°~' + daily['max_degree'] + '°'
    if daily['day_weather'] == daily['night_weather']:
        ss += ' ' + daily['day_weather']
    else:
        ss += ' ' + daily['day_weather'] + \
            '转' + daily['night_weather']
    if daily['day_wind_direction'] == daily['night_wind_direction']:
        ss += ' ' + daily['day_wind_direction']
    else:
        ss += ' ' + daily['day_wind_direction'] + \
            '转' + daily['night_wind_direction']
    if daily['day_wind_power'] == daily['night_wind_power']:
        ss += ' ' + daily['day_wind_power'] + '级'
    else:
        ss += ' ' + daily['day_wind_power'] + \
            '到' + daily['night_wind_power'] + '级'
    wind_direction = {'1': '东北风', '2': '东风', '3': '东南风', '4': '南风',
                      '5': '西南风', '6': '西风', '7': '西北风', '8': '北风'}

    url = 'https://wis.qq.com/weather/common?source=pc&weather_type=air%7Crise&' + \
        '&province=' + city[0] + '&city=' + city[1] + '&county=' + city[2]
    air = s.get(url, headers=headers).json()

    now = data['data']['observe']
    ss += '\n当前天气: ' + now['degree'] + '° ' + now['weather']
    if 'alarm' in data['data']:
        l = []
        for i in data['data']['alarm'].values():
            al = i['type_name'] + i['level_name'] + '预警'
            if not al in l:
                l.append(al)
        for i in l:
            ss += '\n' + i
            
    ss += '\n空气质量指数: ' + str(air['data']['air']['aqi']) + ' ' + air['data']['air']['aqi_name'] + \
        '\n' + wind_direction[now['wind_direction']] + ': ' + now['wind_power'] + '级' +\
        '   湿度: ' + now['humidity'] + '%   气压: ' + now['pressure'] + 'hPa'
    tips = list(data['data']['tips']['observe'].values())
    ss += '\n' + random.choice(tips) + '\n'

    index = list(data['data']['index'].values())
    j = 0
    lit = []
    for i in index:
        if type(i) != dict:
            continue
        lit.append(i['name'] + ': ' + i['info'])
    lit.sort(key=len)
    for i in lit:
        if j % 2 == 0:
            ss += '\n' + i
        else:
            ss += '   ' + i
        j += 1
    ss += '\n\n中央气象台 ' + now['update_time'][8:10] + ':' + now['update_time'][10:] + ' 发布' +\
        '\n数据来源: 腾讯天气'
    await app.sendGroupMessage(group, MessageChain.create([Plain(ss)]))
    pass


async def weather(app, inc, group, member, msg: str):
    t = msg.split(' ')
    if len(t) != 2:
        return
    city = t[1]
    if city == '':
        return

    url = 'https://wis.qq.com/city/like?source=pc&city=' + city
    data = s.get(url, headers=headers).json()

    if not data['data'].values():
        await app.sendGroupMessage(group, MessageChain.create([Plain('切噜~找不到相关位置呢')]))
        return

    lit = list(data['data'].values())
    if len(lit) > 1:
        ss = '有多个相关位置呢，输入id进行选择，输入其他东西会取消查询切噜~：'
        for i in range(1, len(lit) + 1):
            ss += '\n' + str(i) + '：' + lit[i - 1]
        await app.sendGroupMessage(group, MessageChain.create([Plain(ss)]))
        # FIXME 这里尝试了最新版graia提供的interrupt功能，但我总觉得有更好的方法

        @Waiter.create_using_function([GroupMessage])
        async def waiter(event: GroupMessage, waiter_group: Group, waiter_member: Member, waiter_message: MessageChain):
            if waiter_group.id == group.id and waiter_member.id == member.id:
                if is_int(waiter_message.asDisplay()):
                    id = int(waiter_message.asDisplay()) - 1
                    if id >= len(lit) or id < 0:
                        await app.sendGroupMessage(group, MessageChain.create([Plain('查询被取消了切噜噜——')]))
                        return event
                    text = lit[id].split(', ')
                    if len(text) == 2:
                        text.append('')
                    if msg.startswith("天气") or msg.startswith("今日天气") or msg.startswith("1日天气"):
                        await report(app, group, text)
                    elif msg.startswith("昨日天气"):
                        await reporttomorrow(app, group, text, 0)
                    elif msg.startswith("明日天气"):
                        await reporttomorrow(app, group, text, 2)
                    elif msg.startswith("后日天气"):
                        await reporttomorrow(app, group, text, 3)
                    elif is_int(msg[0]):
                        day = int(msg[0])
                        if day < 0 or day > 7:
                            return
                        await reporttomorrow(app, group, text, day)
                else:
                    await app.sendGroupMessage(group, MessageChain.create([Plain('查询被取消了切噜噜——')]))
                return event
        await inc.wait(waiter)

    else:
        text = lit[0].split(', ')
        if len(text) == 2:
            text.append('')
        if msg.startswith("天气") or msg.startswith("今日天气") or msg.startswith("1日天气"):
            await report(app, group, text)
        elif msg.startswith("昨日天气"):
            await reporttomorrow(app, group, text, 0)
        elif msg.startswith("明日天气"):
            await reporttomorrow(app, group, text, 2)
        elif msg.startswith("后日天气"):
            await reporttomorrow(app, group, text, 3)
        elif is_int(msg[0]):
            day = int(msg[0])
            if day < 0 or day > 7:
                return
            await reporttomorrow(app, group, text, day)
