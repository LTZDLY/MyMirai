import requests
import json
import re
from requests_toolbelt import MultipartEncoder

session = requests.Session()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
xcsrftoken = 'vG8h7MUiboOCFyjIBYX0ABdjB7x8F1nfw2fRUkzUGayOzqr7v7DA1SvxBgIT14Sd'


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


# print(login('', ''))
get_problem_by_slug()
get_submissions('two-sum')
get_submission_by_id('')
