import datetime
import json
import random
import re

import requests
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from requests_toolbelt import MultipartEncoder

session = requests.Session()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
xcsrftoken = 'vG8h7MUiboOCFyjIBYX0ABdjB7x8F1nfw2fRUkzUGayOzqr7v7DA1SvxBgIT14Sd'
cookie = "gr_user_id=24d08776-b4d1-41fb-ba9e-f2190e87fb39; _ga=GA1.2.1029641202.1604497028; grwng_uid=d86e6e3d-aca3-473d-93ae-e3c8fcd6e809; __auc=0ffbf1ac1759379b617ee08a9ab; a2873925c34ecbd2_gr_last_sent_cs1=qi-yao-noxiao-lan; csrftoken=vG8h7MUiboOCFyjIBYX0ABdjB7x8F1nfw2fRUkzUGayOzqr7v7DA1SvxBgIT14Sd; __asc=80c05c1017732e58cd16338a9c2; a2873925c34ecbd2_gr_session_id=19089a8a-1220-4e7d-b434-35df1c927be0; a2873925c34ecbd2_gr_last_sent_sid_with_cs1=19089a8a-1220-4e7d-b434-35df1c927be0; a2873925c34ecbd2_gr_session_id_19089a8a-1220-4e7d-b434-35df1c927be0=true; _gid=GA1.2.378276934.1611466644; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuZXh0X2FmdGVyX29hdXRoIjoiLyIsIl9hdXRoX3VzZXJfaWQiOiIyNDA5MDQ2IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJmODg5YmQzMWQ2ZWJlOTlhN2ZhNjMzZGQ0Njg3NjhhYjIyMGJmZjQwY2I0YzEwNzlhZDk0M2UwMGE1ZTEyY2JkIiwiaWQiOjI0MDkwNDYsImVtYWlsIjoiMzQ5NDY4OTU4QHFxLmNvbSIsInVzZXJuYW1lIjoicWkteWFvLW5veGlhby1sYW4iLCJ1c2VyX3NsdWciOiJxaS15YW8tbm94aWFvLWxhbiIsImF2YXRhciI6Imh0dHBzOi8vYXNzZXRzLmxlZXRjb2RlLWNuLmNvbS9hbGl5dW4tbGMtdXBsb2FkL2RlZmF1bHRfYXZhdGFyLnBuZyIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwiX3RpbWVzdGFtcCI6MTYxMTQ2NjY0OS4yNTYzNjU4fQ.RtaKirj6ndvxTzYqSb4Kud4oBSRzYOVNJNrT3xJQbsc; Hm_lvt_fa218a3ff7179639febdb15e372f411c=1609846414,1610018626,1611466641,1611466651; _gat_gtag_UA_131851415_1=1; a2873925c34ecbd2_gr_cs1=qi-yao-noxiao-lan; Hm_lpvt_fa218a3ff7179639febdb15e372f411c=1611466798"


# FIXME 这个功能完全还不能用嘛
def login(username, password):
    url = 'https://leetcode.com'
    cookies = session.get(url).cookies
    for cookie in cookies:
        if cookie.name == 'csrftoken':
            csrftoken = cookie.value

    url = "https://leetcode.com/accounts/login"

    params_data = {
        'csrfmiddlewaretoken': csrftoken,
        'login': username,
        'password': password,
        'next': 'problems'
    }
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', 'Referer':         'https://leetcode.com/accounts/login/',
               "origin": "https://leetcode.com"}
    m = MultipartEncoder(params_data)

    headers['Content-Type'] = m.content_type
    session.post(url, headers=headers, data=m,
                 timeout=10, allow_redirects=False)
    is_login = session.cookies.get('LEETCODE_SESSION') != None
    return is_login


def get_problems():
    url = "https://leetcode.com/api/problems/all/"

    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    resp = session.get(url, headers=headers, timeout=10)

    question_list = json.loads(resp.content.decode('utf-8'))

    for question in question_list['stat_status_pairs']:
        # 题目编号
        question_id = question['stat']['question_id']
        # 题目名称
        question_slug = question['stat']['question__title_slug']
        # 题目状态
        question_status = question['status']

        # 题目难度级别，1 为简单，2 为中等，3 为困难
        level = question['difficulty']['level']

        # 是否为付费题目
        if question['paid_only']:
            continue
        print(question_slug)


def get_problem_by_slug():
    url = "https://leetcode.com/graphql"
    params = {"operationName": "questionOfToday",
              "variables": {},
              "query": "query questionOfToday " '''{
                    todayRecord {
                        question {
                            questionFrontendId
                            questionTitleSlug
                            __typename
                        }
                        lastSubmission {
                            id
                            __typename
                        }
                        date
                        userStatus
                        __typename
                    }
                }
            "}
'''}
    json_data = json.dumps(params).encode('utf8')

    headers = {'cookie': '''gr_user_id=24d08776-b4d1-41fb-ba9e-f2190e87fb39; _ga=GA1.2.1029641202.1604497028; grwng_uid=d86e6e3d-aca3-473d-93ae-e3c8fcd6e809; __auc=0ffbf1ac1759379b617ee08a9ab; a2873925c34ecbd2_gr_last_sent_cs1=qi-yao-noxiao-lan; csrftoken=vG8h7MUiboOCFyjIBYX0ABdjB7x8F1nfw2fRUkzUGayOzqr7v7DA1SvxBgIT14Sd; LEETCODE_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJfYXV0aF91c2VyX2lkIjoiMjQwOTA0NiIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImFsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImY4ODliZDMxZDZlYmU5OWE3ZmE2MzNkZDQ2ODc2OGFiMjIwYmZmNDBjYjRjMTA3OWFkOTQzZTAwYTVlMTJjYmQiLCJpZCI6MjQwOTA0NiwiZW1haWwiOiIzNDk0Njg5NThAcXEuY29tIiwidXNlcm5hbWUiOiJxaS15YW8tbm94aWFvLWxhbiIsInVzZXJfc2x1ZyI6InFpLXlhby1ub3hpYW8tbGFuIiwiYXZhdGFyIjoiaHR0cHM6Ly9hc3NldHMubGVldGNvZGUtY24uY29tL2FsaXl1bi1sYy11cGxvYWQvZGVmYXVsdF9hdmF0YXIucG5nIiwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJfdGltZXN0YW1wIjoxNjA3NzgwOTU2LjYxMjUyNjJ9.REDyncS4LJSD5tV6y0wFrbjvKkuw_EKKodZ1GWi90sw; _gid=GA1.2.1922031332.1608214068; __asc=75d3bf82176756c86b50e72e1a3; Hm_lvt_fa218a3ff7179639febdb15e372f411c=1608214065,1608271439,1608273003,1608287816; a2873925c34ecbd2_gr_session_id=368bb647-75a6-4391-9b67-c193efec66b5; a2873925c34ecbd2_gr_last_sent_sid_with_cs1=368bb647-75a6-4391-9b67-c193efec66b5; a2873925c34ecbd2_gr_session_id_368bb647-75a6-4391-9b67-c193efec66b5=true; _gat_gtag_UA_131851415_1=1; a2873925c34ecbd2_gr_cs1=qi-yao-noxiao-lan; Hm_lpvt_fa218a3ff7179639febdb15e372f411c=1608288632''',
               'User-Agent': user_agent,
               'Content-Type': 'application/json',
               'Referer': 'https://leetcode-cn.com/problemset/all/',
               'x-csrftoken': xcsrftoken}
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    content = resp.json()

    # 题目详细信息
    question = content['data']['question']
    print(question)


def get_submissions(slug):
    url = "https://leetcode.com/graphql"
    '''query getQuestionTranslation($lang: String) {
        translations: allAppliedQuestionTranslations(lang: $lang) {
            title
            questionId
            __typename
            }
        }
    '''
    params = {'getQuestionTranslation': "Submissions",
              'variables': {"offset": 0, "limit": 20, "lastKey": '', "questionSlug": slug},
              'query': '''query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
                submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
                lastKey
                hasNext
                submissions {
                    id
                    statusDisplay
                    lang
                    runtime
                    timestamp
                    url
                    isPending
                    __typename
                }
                __typename
            }
        }'''
              }

    json_data = json.dumps(params).encode('utf8')

    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', 'Referer': 'https://leetcode.com/accounts/login/',
               "Content-Type": "application/json"}
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    content = resp.json()
    for submission in content['data']['submissionList']['submissions']:
        print(submission)


def get_submission_by_id(submission_id):
    url = "https://leetcode.com/submissions/detail/" + submission_id
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
               "Content-Type": "application/json"}
    code_content = session.get(url, headers=headers, timeout=10)

    pattern = re.compile(
        r'submissionCode: \'(?P<code>.*)\',\n  editCodeUrl', re.S)
    m1 = pattern.search(code_content.text)
    code = m1.groupdict()['code'] if m1 else None
    print(code)


def get_question_by_id(question_id: str):
    # 接受的参数为题目的真正id
    # 返回题目的相关json数据
    url = "https://leetcode-cn.com/api/problems/all/"
    a = requests.get(url)
    l = a.json()["stat_status_pairs"]
    for i in l:
        if str(i['stat']['question_id']) == question_id:
            return i
    else:
        return 'no found'


def get_question_translation(question_id: str):
    # 接受的参数为题目的真正id
    # 返回题目的中文标题
    url = "https://leetcode-cn.com/graphql"
    data = {
        "operationName": "getQuestionTranslation",
        "query": '''query getQuestionTranslation($lang: String) {
            translations: allAppliedQuestionTranslations(lang: $lang) {
                title
                questionId
                __typename
            }
        }''',
        "variables": {}
    }
    a = requests.post(url, json=data)
    l = a.json()['data']['translations']
    for i in l:
        if i['questionId'] == question_id:
            return i['title']
    else:
        return 'no found'


def get_daily_questions():
    # 返回每日一题的真正id
    t = datetime.datetime.now()
    url = "https://leetcode-cn.com/graphql"
    data = {
        "operationName": "dailyQuestionRecords",
        "query": '''query dailyQuestionRecords($year: Int!, $month: Int!) {
            dailyQuestionRecords(year: $year, month: $month) {
                date
                question {
                    questionId
                    questionFrontendId
                    questionTitle
                    questionTitleSlug
                    translatedTitle
                    __typename
                }
                userStatus
                __typename
            }
        }''',
        "variables": {"year": t.year, "month": t.month}
    }
    headers = {'cookie': cookie,
               'user-Agent': user_agent,
               'content-Type': 'application/json',
               'referer': 'https://leetcode-cn.com/problemset/all/',
               'x-csrftoken': xcsrftoken}
    a = requests.post(url, headers=headers, json=data)
    return a.json()['data']['dailyQuestionRecords'][0]['question']['questionId']


async def get_daily(app, group):
    id = get_daily_questions()
    data = get_question_by_id(id)
    tran = get_question_translation(id)

    dif = data['difficulty']['level']
    if dif == 1:
        dif = '简单'
    elif dif == 2:
        dif = '中等'
    elif dif == 3:
        dif = '困难'

    s = "LeetCode 每日一题" +\
        "\n题号：" + data['stat']['frontend_question_id'] +\
        "\n标题：" + data['stat']['question__title'] +\
        "\n翻译：" + tran +\
        "\n难度：" + dif +\
        "\n通过率：" + '{:.2%}'.format(int(data['stat']['total_acs'])/int(data['stat']['total_submitted'])) +\
        "\n地址：" + 'https://leetcode-cn.com/problems/' + \
        data['stat']['question__title_slug']

    await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))


async def get_rand(app, group):
    url = "https://leetcode-cn.com/api/problems/all/"
    a = requests.get(url)
    l = a.json()["stat_status_pairs"]
    d = random.choice(l)
    id = str(d['stat']['question_id'])
    tran = get_question_translation(id)

    dif = d['difficulty']['level']
    if dif == 1:
        dif = '简单'
    elif dif == 2:
        dif = '中等'
    elif dif == 3:
        dif = '困难'

    s = "LeetCode 随机一题" +\
        "\n题号：" + d['stat']['frontend_question_id'] +\
        "\n标题：" + d['stat']['question__title'] +\
        "\n翻译：" + tran +\
        "\n难度：" + dif +\
        "\n通过率：" + '{:.2%}'.format(int(d['stat']['total_acs'])/int(d['stat']['total_submitted'])) +\
        "\n地址：" + 'https://leetcode-cn.com/problems/' + \
        d['stat']['question__title_slug']

    await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))


async def luogu_rand(app, group):
    url = 'https://www.luogu.com.cn/problem/list?_contentOnly=1'
    headers = {
        'user-Agent': user_agent
    }
    data = requests.get(url, headers=headers).json()
    print(data)
    page = int(data['currentData']['problems']['count'] /
               data['currentData']['problems']['perPage'])
    p = random.randint(0, page + 1)
    url = 'https://www.luogu.com.cn/problem/list?_contentOnly=1&page=%d' % p
    data = requests.get(url, headers=headers).json()
    d = random.choice(data['currentData']['problems']['result'])
    print(d)
    dif = d['difficulty']
    l = ['暂无评定','入门','普及-','普及/提高-','普及+/提高','提高+/省选-','省选/NOI-','NOI/NOI+/CTSC']
    s = "luogu 随机一题" +\
        "\n题号：" + d['pid'] +\
        "\n标题：" + d['title'] +\
        "\n难度：" + l[dif] +\
        "\n通过率：" + '{:.2%}'.format(int(d['totalAccepted'])/int(d['totalSubmit'])) +\
        "\n地址：" + 'https://www.luogu.com.cn/problem/' + d['pid']
    await app.sendGroupMessage(group, MessageChain.create([Plain(s)]))

# print(get_question_by_id('1'))
# print(get_question_translation('1'))
# print(get_daily_questions())
