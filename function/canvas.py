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


def get_id(member_id: int) -> int:
    Localpath = './data/tongji.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    for i in data["data"]:
        if i['qq'] == member_id:
            return i['user_id']
    else:
        raise 'error'


def createlink(qq: int) -> Session:
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

    s = requests.session()
    s.get('https://ids.tongji.edu.cn:8443')
    code = ''
    with s.get('https://ids.tongji.edu.cn:8443/nidp/app/login?flag=true') as code_img:
        code = s.post('http://172.81.215.215/pi/crack',
                      json={'data_url': code_img.text}).json()['ans']

    data = {'option': 'credential', 'Ecom_User_ID': Ecom_User_ID,
            'Ecom_Password': Ecom_Password, 'Ecom_code': code}

    s.post('https://ids.tongji.edu.cn:8443/nidp/app/login', data=data)
    s.get('http://canvas.tongji.edu.cn/login')
    return s


def is_session(s: Session, member_id: int) -> Session:
    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))
    if 'error' in data:
        print("检测到canvas登录状态丢失，现尝试重新登录canvas")
        s = createlink(member_id)
    return s


def add_person(qq_id, id, password):
    s = requests.session()
    s.get('https://ids.tongji.edu.cn:8443')
    code = ''
    with s.get('https://ids.tongji.edu.cn:8443/nidp/app/login?flag=true') as code_img:
        code = s.post('http://172.81.215.215/pi/crack',
                      json={'data_url': code_img.text}).json()['ans']

    data = {'option': 'credential', 'Ecom_User_ID': id,
            'Ecom_Password': password, 'Ecom_code': code}

    sss = (s.post('https://ids.tongji.edu.cn:8443/nidp/app/login', data=data)).text

    if sss.find("账号状态需要更新，请先执行更新操作！") != -1:
        raise 'error'

    user_id = 0
    soup = BeautifulSoup(
        s.get('http://canvas.tongji.edu.cn/login').text, features="html.parser")
    lit = soup.body['class']
    for i in lit:
        if i.startswith('context-user_'):
            user_id = int(i.replace('context-user_', ''))

    lit = soup.find('img')
    name = lit['alt']
    dit = {'name': name, 'qq': qq_id, 'id': id,
           'password': password, 'user_id': user_id}

    Localpath = './data/tongji.json'
    data = {}
    fr = open(Localpath, encoding='utf-8')
    data = json.load(fr)
    fr.close()

    data['data'].append(dit)

    with open(Localpath, "w") as fw:
        jsObj = json.dumps(data)
        fw.write(jsObj)
        fw.close()
    pass


def calender(member):  # 这块好像并没有使用需求
    s = createlink(member.id)
    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events?type=assignment&context_codes%5B%5D=course_30663&context_codes%5B%5D=course_31391&start_date=2020-10-25T16%3A00%3A00.000Z&end_date=2021-02-06T16%3A00%3A00.000Z&per_page=50&context_codes%5B%5D=user_' + \
        str(get_id(member.id))
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


async def timetable(app, s, group, member, flag=True):
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


async def addddl(app, s, group, member, msg: str):
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
            'calendar_event[location_name]': event_local, 'calendar_event[context_code]': 'user_' + str(get_id(member.id)), '_method': _method,
            'authenticity_token': parse.unquote(requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}

    r = s.post(url, data=data)

    if not is_json(r.text) or 'errors' in r.json():
        await app.sendGroupMessage(group, MessageChain.create([Plain('添加失败！')]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('添加成功！')]))


async def delddl(app, s, group, member, msg: str):
    text = msg.split(' ')
    if len(text) == 1:
        await app.sendGroupMessage(group, MessageChain.create([Plain('请输入标题！')]))
    elif len(text) != 2:
        return

    event_title = text[1]

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


async def markfinish(app, s: Session, group, member, msg: str):

    text = msg.split(' ')
    if len(text) == 1:
        await app.sendGroupMessage(group, MessageChain.create([Plain('请输入标题！')]))
    elif len(text) != 2:
        return

    event_title = text[1]

    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))

    plannable_id = ''
    event_id = None

    for i in data:
        if i['context_type'] == 'User' and i['plannable']['title'] == event_title:
            plannable_id = i['plannable_id']
            if i['planner_override'] != None:
                event_id = i['planner_override']['id']
            break
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('查无此事件，请检查标题是否输入正确')]))

    data = {'id': event_id, 'marked_complete': True, 'plannable_id': plannable_id,
            'plannable_type': 'calendar_event', 'user_id': get_id(member.id),
            'authenticity_token': parse.unquote(requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}
    if event_id == None:
        url = 'http://canvas.tongji.edu.cn/api/v1/planner/overrides'
        r = s.post(url, data=data)
    else:
        url = 'http://canvas.tongji.edu.cn/api/v1/planner/overrides/' + \
            str(event_id)
        r = s.put(url, data=data)

    if not is_json(r.text) or 'errors' in r.json():
        await app.sendGroupMessage(group, MessageChain.create([Plain('标记为完成失败！')]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([Plain('标记为完成成功！')]))


def markunfinsh():
    """
    docstring
    """
    pass


async def canvas(app, group, member, msg, s: Session):
    s = is_session(s, member.id)
    if (member.id == 349468958 or member.id == 5980403) and msg == 'canvas.todo':
        await timetable(app, s, group, member)
    if (member.id == 349468958 or member.id == 5980403) and msg == 'canvas.todo.finish':
        await timetable(app, s, group, member, False)
    if (member.id == 349468958 or member.id == 5980403) and msg.startswith('canvas.todo.add'):
        await addddl(app, s, group, member, msg)
    if (member.id == 349468958 or member.id == 5980403) and msg.startswith('canvas.todo.del'):
        await delddl(app, s, group, member, msg)
    if (member.id == 349468958 or member.id == 5980403) and msg.startswith('canvas.todo.makfin'):
        await markfinish(app, s, group, member, msg)

if __name__ == '__main__':
    add_person(1, 1951096, 'LAN*150019')
    pass
