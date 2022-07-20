import json
import datetime
from urllib import parse

import requests
from bs4 import BeautifulSoup
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from requests.sessions import Session

from .crack import crack_main


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
        raise Exception("账号未记录")


# 登录分为三块，统一身份认证，canvas登录，course登录
def ids_login(qq: int) -> Session:
    """统一身份认证登录"""
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
        raise Exception("账号未记录")

    s = requests.session()
    while(1):
        try:
            code = crack_main(s)
            break
        except:
            print("裂了")
            pass
    if code == None:
        raise Exception("验证码错误")

    data = {'option': 'credential', 'Ecom_User_ID': Ecom_User_ID,
            'Ecom_Password': Ecom_Password, 'Ecom_Captche': code}

    s.post('https://ids.tongji.edu.cn:8443/nidp/app/login', data=data)
    return s


# 第二部分，canvas登录，只需要一行代码
def canvas_login(s: Session) -> Session:
    """canvas登录"""
    s.get('http://canvas.tongji.edu.cn/login')
    return s


courses_data = {}


# 第三部分，courses登录
def courses_login(s: Session, qq: int) -> Session:
    """courses登录"""
    ss = s.get("https://ids.tongji.edu.cn:8443/nidp/oauth/nam/authz?scope=profile&response_type=code&redirect_uri=https%3A%2F%2Fcourses.tongji.edu.cn%2Fsign-in&client_id=241129f4-7528-4207-8751-ee240727b41c")
    code = ss.url.split("code=")[1].split("&")[0]
    data = {"user_token": None, "code": code}
    ss = s.post("https://courses.tongji.edu.cn/tmbs/api/v1/sso", data=data)
    token = ss.json()["data"]["token"]
    courses_data[qq] = (code, token)
    print(courses_data[qq])
    return s


# ids登录失效检测
def ids_session(s: Session, qq: int) -> Session:
    ss = s.post('https://ids.tongji.edu.cn:8443/nidp/app/login')
    print(ss.text)
    t = ss.text
    if t.find("document.forms[0].submit()") != -1:
        print("检测到统一身份认证登录状态丢失，现尝试重新登录统一身份认证")
        s.close()
        return ids_login(qq)
    else:
        return s


# canvas登录失效检测
def canvas_session(s: Session, qq: int):
    url = f"http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date={datetime.datetime.now().strftime('%Y-%m-%d')}"
    r = s.get(url)
    if r.status_code == 401:
        print("检测到canvas登录状态丢失，现尝试重新登录canvas")
        s = ids_session(s, qq)
        return canvas_login(s)
    else:
        return s


# courses登录失效检测
def courses_session(s: Session, qq: int):
    if qq not in courses_data:
        s = ids_session(s, qq)
        return courses_login(s, qq)
    
    token = courses_data[qq][1]
    date = datetime.datetime.now().date()
    data = {"user_token": token, "start": date, "end": date}
    url = "https://courses.tongji.edu.cn/tmbs/api/v1/user/calendar/my"
    r = s.post(url, data=data)
    if r.status_code == 401:
        print("检测到courses登录状态丢失，现尝试重新登录courses")
        s = ids_session(s, qq)
        return courses_login(s, qq)
    else:
        return s


def add_person(qq_id, id, password):
    s = requests.session()
    s.get('https://ids.tongji.edu.cn:8443')

    code = crack_main(s)
    if code == None:
        raise Exception("验证码错误")

    data = {'option': 'credential', 'Ecom_User_ID': id,
            'Ecom_Password': password, 'Ecom_Captche': code}

    sss = (s.post('https://ids.tongji.edu.cn:8443/nidp/app/login', data=data)).text

    if sss.find("账号状态需要激活，请先执行激活操作！") != -1:
        raise Exception("密码错误")

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


# def calender(member):  # 这块好像并没有使用需求
#     s = createlink(member.id)
#     url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events?type=assignment&context_codes%5B%5D=course_30663&context_codes%5B%5D=course_31391&start_date=2020-10-25T16%3A00%3A00.000Z&end_date=2021-02-06T16%3A00%3A00.000Z&per_page=50&context_codes%5B%5D=user_' + \
#         str(get_id(member.id))
#     r = s.get(url)
#     data = json.loads(r.text.replace('while(1);', ''))
#     s = ''
#     for i in data:
#         s += '\n标题：' + i['title']
#         if 'assignment_overrides' in i:
#             s += '\n课程：' + i['assignment_overrides'][0]['title']
#         s += '\nddl：' + i['all_day_date']
#         if i['created_at'][:10] == i['updated_at'][:10]:
#             s += '（未完成）'
#         else:
#             s += '（已完成）'
#     print(s)
#     pass


async def timetable(app, s, group, member, flag=True):
    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))
    sstr = ''
    ss = ''
    for i in data:
        if not 'context_type' in i:
            continue
        date = datetime.datetime.strptime(
            i['plannable_date'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
        if (date - datetime.datetime.now()).days > 30:
            continue
        if i['context_type'] == 'User':
            if flag and i['planner_override'] != None and i['planner_override']['marked_complete'] != False:
                continue
            ss += '\n标题：' + i['plannable']['title'] + \
                '\nddl：' + date.strftime('%Y-%m-%d %H:%M:%S')
            if i['planner_override'] != None and i['planner_override']['marked_complete'] != False:
                ss += '（已标记完成）'
        elif i['context_type'] == 'Course':
            if flag and 'submissions' in i:
                sub = i['submissions']
                if (type(sub) == bool and sub == True) or (type(sub) == dict and sub['submitted'] == True):
                    continue
            sstr += '\n标题：' + i['plannable']['title'] + \
                '\n课程：' + i['context_name'] + \
                '\nddl：' + date.strftime('%Y-%m-%d %H:%M:%S')
            if 'submissions' in i:
                sub = i['submissions']
                if (type(sub) == bool and sub == True) or (type(sub) == dict and sub['submitted'] == True):
                    sstr += '（已完成）'
    if sstr == '':
        sstr = '\n一月内的所有任务已经全部完成了呢！'
    if ss == '':
        ss = '\n一月内的所有任务已经全部完成了呢！'
    sstr = '一月内课程ddl：' + sstr + '\n一月内自定ddl：' + ss
    await app.send_group_message(group, MessageChain([Plain(sstr)]))
    pass


async def addddl(app, s, group, member, msg: str):
    event_title = ''
    event_start = ''
    event_end = ''
    event_local = ''
    _method = 'POST'

    text = msg.split(' ')

    if len(text) == 1:
        await app.send_group_message(group, MessageChain([Plain('请输入标题！')]))
    elif len(text) == 2:
        event_end = event_start = (
            datetime.datetime.now() - datetime.timedelta(hours=8) + datetime.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    event_title = text[1]
    if event_start == '':
        text[2] = text[2].replace('-', '.')
        y = datetime.datetime.now().year
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
            datetime.datetime(int(y), int(m), int(d)) - datetime.timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%SZ')

    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events'

    data = {'calendar_event[title]': event_title, 'calendar_event[start_at]': event_start, 'calendar_event[end_at]': event_end,
            'calendar_event[location_name]': event_local, 'calendar_event[context_code]': 'user_' + str(get_id(member.id)), '_method': _method,
            'authenticity_token': parse.unquote(requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}

    r = s.post(url, data=data)

    if not is_json(r.text) or 'errors' in r.json():
        await app.send_group_message(group, MessageChain([Plain('添加失败！')]))
    else:
        await app.send_group_message(group, MessageChain([Plain('添加成功！')]))


async def delddl(app, s, group, member, msg: str):
    text = msg.split(' ')
    if len(text) == 1:
        await app.send_group_message(group, MessageChain([Plain('请输入标题！')]))
    elif len(text) != 2:
        return

    event_title = text[1]

    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.datetime.now().strftime('%Y-%m-%d')
    r = s.get(url)
    data = json.loads(r.text.replace('while(1);', ''))

    event_id = 0

    for i in data:
        if i['context_type'] == 'User' and i['plannable']['title'] == event_title:
            event_id = int(i['plannable_id'])
            break
    else:
        await app.send_group_message(group, MessageChain([Plain('查无此事件，请检查标题是否输入正确')]))

    url = 'http://canvas.tongji.edu.cn/api/v1/calendar_events/' + str(event_id)
    data = {'_method': 'DELETE', 'authenticity_token': parse.unquote(
        requests.utils.dict_from_cookiejar(s.cookies)['_csrf_token'])}
    r = s.post(url, data=data)
    if not is_json(r.text) or 'errors' in r.json():
        await app.send_group_message(group, MessageChain([Plain('删除失败！')]))
    else:
        await app.send_group_message(group, MessageChain([Plain('删除成功！')]))


async def markfinish(app, s: Session, group, member, msg: str):

    text = msg.split(' ')
    if len(text) == 1:
        await app.send_group_message(group, MessageChain([Plain('请输入标题！')]))
    elif len(text) != 2:
        return

    event_title = text[1]

    url = 'http://canvas.tongji.edu.cn/api/v1/planner/items?per_page=50&start_date=' + \
        datetime.datetime.now().strftime('%Y-%m-%d')
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
        await app.send_group_message(group, MessageChain([Plain('查无此事件，请检查标题是否输入正确')]))

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
        await app.send_group_message(group, MessageChain([Plain('标记为完成失败！')]))
    else:
        await app.send_group_message(group, MessageChain([Plain('标记为完成成功！')]))


def markunfinsh():
    """
    docstring
    """
    pass


async def courses_calender(app, s, group, member):
    token = courses_data[member.id][1]
    date = datetime.now().date()
    data = {"user_token": token, "start": date, "end": date}
    c = s.post(
        "https://courses.tongji.edu.cn/tmbs/api/v1/user/calendar/my", data=data)
    cc = c.json()["data"]
    cc.sort(key=lambda x: x['start'])
    sstr = ""
    for i in cc:
        sstr += f"{i['start'][11:16]} - {i['end'][11:16]}\n"
        sstr += i['title']
        sstr += '\n\n'
    await app.send_group_message(group, MessageChain([Plain(sstr[:-2])]))


async def canvas(app, group, member, msg, s: Session):
    try:
        s = canvas_session(s, member.id)
    except Exception as e:
        if str(e) == "验证码错误":
            await app.send_group_message(group, MessageChain([Plain(
                '登录超时，请稍后再试。'
            )]))
        return
    if msg == 'canvas.todo':
        await timetable(app, s, group, member)
    if msg == 'canvas.todo.finish':
        await timetable(app, s, group, member, False)
    if msg.startswith('canvas.todo.add'):
        await addddl(app, s, group, member, msg)
    if msg.startswith('canvas.todo.del'):
        await delddl(app, s, group, member, msg)
    if msg.startswith('canvas.todo.makfin'):
        await markfinish(app, s, group, member, msg)


async def courses(app, group, member, msg, s: Session):
    # 不需要登录

    # 需要登录
    try:
        s = courses_session(s, member.id)
    except Exception as e:
        if str(e) == "验证码错误":
            await app.send_group_message(group, MessageChain([Plain(
                '登录超时，请稍后再试。'
            )]))
        return
    if msg == 'courses.today':
        await courses_calender(app, s, group, member)

# if __name__ == "__main__":
#     s = createlink(349468958)
#     pass
