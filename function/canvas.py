import asyncio
import json
from datetime import datetime, timedelta
from urllib import parse

import requests
from bs4 import BeautifulSoup
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from requests.sessions import Session


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def createlink(qq: int) -> Session:
    s = requests.session()
    aaaaa = s.get('http://canvas.tongji.edu.cn/login/openid_connect')
    soup = BeautifulSoup(aaaaa.text, 'html.parser')
    a = s.get('https://ids.tongji.edu.cn:8443' + soup.form['action'])

    b = s.get('https://ids.tongji.edu.cn:8443/nidp/app/login?flag=true')
    code = s.post('http://172.81.215.215/pi/crack',
                  json={'data_url': b.text}).json()['ans']

    Ecom_User_ID = 0
    Ecom_Password = ''

    Localpath = './data/tongji.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    for i in data["data"]:
        if i['qq'] == qq:
            Ecom_User_ID = i['id']
            Ecom_Password = i['password']
            break
    else:
        raise 'error'

    data = {'option': 'credential', 'Ecom_User_ID': Ecom_User_ID,
            'Ecom_Password': Ecom_Password, 'Ecom_code': code}
    ans = s.post(
        'https://ids.tongji.edu.cn:8443/nidp/app/login', data=data)

    text = soup.form['action'].split('&')
    ttext = text[4].split(parse.quote('?'))
    url = (parse.unquote(ttext[0]) + '?' + ttext[1])[7:]
    url = url.replace(parse.quote('='), '=').replace(parse.quote('&'), '&')
    af = s.get(url)
    return s

# 这块好像并没有使用需求


def calender(member):
    s = createlink(member.id)
    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events?type=assignment&context_codes%5B%5D=user_233046&context_codes%5B%5D=course_30663&context_codes%5B%5D=course_31391&start_date=2020-10-25T16%3A00%3A00.000Z&end_date=2021-02-06T16%3A00%3A00.000Z&per_page=50'
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))
    s = ''
    for i in data:
        s += '\n标题：' + i['title']
        if 'assignment_overrides' in i:
            s += '\n课程：' + i['assignment_overrides'][0]['title']
        s += '\nddl：' + i['all_day_date']
        if i['created_at'][:10] == i['updated_at'][:10]:
            s += '（未完成）'
        else:
            s += '（已完成）'
    print(s)
    pass


async def timetable(app, group, member, flag=True):
    s = createlink(member.id)
    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))
    sstr = ''
    ss = ''
    for i in data:
        if not 'context_type' in i:
            continue
        date = datetime.strptime(
            i['plannable_date'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=8)
        if (date - datetime.now()).days > 30:
            continue
        if i['context_type'] == 'User':
            if flag and i['planner_override'] != None and i['planner_override']['marked_complete'] != False:
                continue
            ss += '\n标题：' + i['plannable']['title'] + \
                '\nddl：' + date.strftime('%Y-%m-%d %H:%M:%S')
            if i['planner_override'] != None and i['planner_override']['marked_complete'] != False:
                ss += '（已标记完成）'
        elif i['context_type'] == 'Course':
            if flag and i['submissions']['submitted'] == True:
                continue
            sstr += '\n标题：' + i['plannable']['title'] + \
                '\n课程：' + i['context_name'] + \
                '\nddl：' + date.strftime('%Y-%m-%d %H:%M:%S')
            if i['submissions']['submitted'] == True:
                sstr += '（已完成）'
    if sstr == '':
        sstr = '\n一月内的所有任务已经全部完成了呢！'
    if ss == '':
        ss = '\n一月内的所有任务已经全部完成了呢！'
    sstr = '一月内课程ddl：' + sstr + '\n一月内自定ddl：' + ss
    await app.sendGroupMessage(group, MessageChain.create([Plain(sstr)]))
    pass


async def addddl(app, group, member, msg: str):
    event_title = ''
    event_start = ''
    event_end = ''
    event_local = ''
    _method = 'POST'

    text = msg.split(' ')

    if len(text) == 1:
        await app.sendGroupMessage(group, MessageChain.create([Plain('请输入标题！')]))
    elif len(text) == 2:
        event_end = event_start = (
            datetime.now() - timedelta(hours=8) + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    event_title = text[1]
    if event_start == '':
        text[2] = text[2].replace('-', '.')
        y = datetime.now().year
        m = 0
        d = 0
        subtext = text[2].split('.')
        if len(subtext) == 3:
            y = subtext[0]
            m = subtext[1]
            d = subtext[2]
        elif len(subtext) == 2:
            m = subtext[0]
            d = subtext[1]
        else:
            return
        event_end = event_start = (
            datetime(int(y), int(m), int(d)) - timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%SZ')

    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events'

    s = createlink(member.id)
    aaaa = requests.utils.dict_from_cookiejar(s.cookies)

    data = {'calendar_event[title]': event_title, 'calendar_event[start_at]': event_start, 'calendar_event[end_at]': event_end,
            'calendar_event[location_name]': event_local, 'calendar_event[context_code]': 'user_233046', '_method': _method,
            'authenticity_token': parse.unquote(requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}

    r = s.post(url, data=data)

    if not is_json(r.text) or 'errors' in r.json():
        await app.sendGroupMessage(group, MessageChain.create([Plain('添加失败！')]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('添加成功！')]))


async def delddl(app, group, member, msg: str):
    text = msg.split(' ')
    if len(text) == 1:
        await app.sendGroupMessage(group, MessageChain.create([Plain('请输入标题！')]))
    elif len(text) != 2:
        return

    event_title = text[1]

    s = createlink(member.id)

    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))

    event_id = 0

    for i in data:
        if i['context_type'] == 'User' and i['plannable']['title'] == event_title:
            event_id = int(i['plannable_id'])
            break
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('查无此事件，请检查标题是否输入正确')]))

    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events/' + str(event_id)
    data = {'_method': 'DELETE', 'authenticity_token': parse.unquote(
        requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}
    r = s.post(url, data=data)
    if not is_json(r.text) or 'errors' in r.json():
        await app.sendGroupMessage(group, MessageChain.create([Plain('删除失败！')]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('删除成功！')]))


def markfinish():
    """
    docstring
    """
    pass


def markunfinsh():
    """
    docstring
    """
    pass


async def canvas(app, group, member, msg):
    try:
        if (member.id == 349468958 or member.id == 5980403) and msg == 'canvas.todo':
            await timetable(app, group, member)
        if (member.id == 349468958 or member.id == 5980403) and msg == 'canvas.todo.finish':
            await timetable(app, group, member, False)
        if (member.id == 349468958 or member.id == 5980403) and msg.startswith('canvas.todo.add'):
            await addddl(app, group, member, msg)
        if (member.id == 349468958 or member.id == 5980403) and msg.startswith('canvas.todo.del'):
            await delddl(app, group, member, msg)
        pass
    except:
        await app.sendGroupMessage(group, MessageChain.create([Plain(
            '并没有记录任何学号信息，如需使用此功能请私聊向bot申请。\n注意：该功能需要用户提供统一身份认证的学号和密码以登录canvas。'
        )]))
        pass

if __name__ == '__main__':
    delddl()
    pass
