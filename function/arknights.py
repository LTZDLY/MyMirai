from itertools import combinations
import json
import time

# from function.aliyun import Sample

with open('data/arknightsstages.json', 'r', encoding='utf8')as fp:
    ark_stages = json.load(fp)
with open('data/arknightsmatrix.json', 'r', encoding='utf8')as fp:
    ark_matrix = json.load(fp)
with open('data/arknightscharacter.json', 'r', encoding='utf8')as fp:
    ark_character = json.load(fp)

tags = ['先锋干员', '近卫干员', '狙击干员', '重装干员', '医疗干员', '辅助干员', '术师干员', '特种干员', '近战位', '远程位', '新手', '资深干员',
        '高级资深干员', '治疗', '支援', '输出', '群攻', '减速', '生存', '防护', '削弱', '位移', '控场', '爆发', '召唤', '快速复活', '费用回复', '支援机械']


def short2name(ark_items, short: str) -> str:
    for i in ark_items:
        if 'short' in i and short in i["short"]:
            return i["name"]
    return short


def search_stages(stage_name: str, all=False):
    '''
    查询关卡掉落
    '''
    with open('data/arknightsitems.json', 'r', encoding='utf8')as fp:
        ark_items = json.load(fp)
    for i in ark_stages:
        if i['code'] == stage_name:
            stageId = i['stageId']
            apCost = i['apCost']
            break
    else:
        return "什么都没查到哦~"

    ans = []
    l = {}
    flag = False
    for i in ark_matrix['matrix']:
        if flag and i['stageId'] != stageId:
            break
        elif i['stageId'] == stageId:
            flag = True
            if not all and not i['itemId'].isdigit():
                continue
            ans.append(i)
            l[i['itemId']] = len(l)

    for i in ark_items:
        if i['itemId'] in l:
            ans[l[i['itemId']]]['name'] = i['name']

    out = []
    for i in ans:
        temp = {}
        temp['物品'] = i['name']
        temp['样本数'] = i['times']
        temp['掉落数'] = i['quantity']
        temp['百分比'] = i['quantity'] / i['times']
        temp['单件期望理智'] = apCost / temp['百分比']
        temp['统计区间'] = time.strftime('%Y-%m-%d', time.localtime(i['start'] / 1000)) + \
            (' 至今' if i['end'] == None else
             (' ~ ' + time.strftime('%Y-%m-%d', time.localtime(i['end'] / 1000))))
        out.append(temp)
    out.sort(key=lambda x: x['百分比'], reverse=True)
    # print(out)

    s = ''
    for i in out:
        s += f"物品：{i['物品']}\n样本数：{i['样本数']}，掉落数：{i['掉落数']}\n"
        s += "百分比：{:.2%}，单件期望理智：{:.2f}\n".format(i['百分比'], i['单件期望理智'])
        s += f"统计区间：{i['统计区间']}\n"
    return (s[:-1])


def search_items(item: str, end=5, start=0):
    with open('data/arknightsitems.json', 'r', encoding='utf8')as fp:
        ark_items = json.load(fp)
    item = short2name(ark_items, item)
    ans = []
    for i in ark_items:
        if i['name'] == item:
            itemId = i['itemId']
            break
    else:
        return "什么都没查到哦~"

    l = {}
    for i in ark_matrix['matrix']:
        if i['itemId'] == itemId:
            if i['quantity'] == 0:
                continue
            ans.append(i)
            l[i['stageId']] = len(l)

    for i in ark_stages:
        if i['stageId'] in l:
            ans[l[i['stageId']]]['code'] = i['code']
            ans[l[i['stageId']]]['apCost'] = i['apCost']

    # print(ans)
    out = []
    for i in ans:
        temp = {}
        temp['作战'] = i['code']
        temp['样本数'] = i['times']
        temp['掉落数'] = i['quantity']
        temp['百分比'] = i['quantity'] / i['times']
        temp['理智'] = i['apCost']
        temp['单件期望理智'] = i['apCost'] / temp['百分比']
        temp['统计区间'] = time.strftime('%Y-%m-%d', time.localtime(i['start'] / 1000)) + \
            (' 至今' if i['end'] == None else
             (' ~ ' + time.strftime('%Y-%m-%d', time.localtime(i['end'] / 1000))))
        out.append(temp)
    out.sort(key=lambda x: x['单件期望理智'])
    # print(out)

    s = ''
    for i in out[start:end]:
        s += f"{i['作战']}\n样本数：{i['样本数']}，掉落数：{i['掉落数']}，"
        s += "百分比：{:.2%}\n".format(i['百分比'])
        s += '' if i['理智'] > 50 else "理智：{}，单件期望理智：{:.2f}\n".format(
            i['理智'], i['单件期望理智'])
        s += f"统计区间：{i['统计区间']}\n"
    return (s[:-1])


def arksetDefine(msg):
    text = msg.split(' ')
    if(len(text) != 3):
        return
    Localpath = 'data/arknightsitems.json'
    with open(Localpath, 'r', encoding='utf8')as fp:
        ark_items = json.load(fp)
    wanna = short2name(ark_items, text[1])
    for i in ark_items:
        if wanna == i["name"]:
            if not 'short' in i:
                i['short'] = []
            if not text[2] in i["short"]:
                i["short"].append(text[2])
                with open(Localpath, "w", encoding='utf8') as fw:
                    jsObj = json.dumps(ark_items)
                    fw.write(jsObj)
                    fw.close()
                return "添加缩写：" + wanna + " 缩写为 " + text[2]
            break
    else:
        return "什么都没查到哦~"


def arkoffDefine(msg):
    text = msg.split(' ')
    if(len(text) != 3):
        return
    Localpath = 'data/arknightsitems.json'
    with open(Localpath, 'r', encoding='utf8')as fp:
        ark_items = json.load(fp)
    wanna = short2name(ark_items, text[1])
    for i in ark_items:
        if wanna == i["name"]:
            if not 'short' in i:
                i['short'] = []
            if text[2] in i["short"]:
                i["short"].remove(text[2])
                with open(Localpath, "w", encoding='utf8') as fw:
                    jsObj = json.dumps(ark_items)
                    fw.write(jsObj)
                    fw.close()
                return "删除缩写：" + wanna + " 缩写为 " + text[2]
            else:
                return wanna + "没有这个缩写哦！"
    else:
        return "什么都没查到哦~"


def arkexpand(msg: str):
    text = msg.split(' ')
    if(len(text) != 2):
        return
    Localpath = 'data/arknightsitems.json'
    with open(Localpath, 'r', encoding='utf8')as fp:
        ark_items = json.load(fp)
    wanna = short2name(ark_items, text[1])
    if wanna != text[1]:
        return text[1] + " 可能是 " + wanna + " 的缩写"
    else:
        return "并未查到是什么的缩写，是本名也说不定哦！"


def fun(d):
    return list(d.keys())[0]


# def arkRecruit(url):
#     data = Sample.main(url)
#     data = json.loads(data)
#     text = data['content'].split(' ')
#     ans = []
#     for i in text:
#         if i in tags:
#             ans.append(i)
#     # ans = ['远程位', '医疗干员', '生存', '防护', '输出']
#     left = []
#     right = []
#     for i in range(1,6):
#         for c in combinations(ans, i):
#             left.append(c)
            
#     for i in left:
#         l = [i for i in range(99)]
#         for j in i:
#             if not l:
#                 break
#             else:
#                 l = [m for m in l if m in ark_character['data'][j]]
#         # print(i, l)
#         right.append(l)
#         # output.append({i: ark_character['data'][i]})
#     rright = []
#     d = {}
#     for i in range(len(right)):
#         temp = []
#         for j in range(len(right[i])):
#             right[i][j] = ark_character['characters'][right[i][j]]
#             if (right[i][j]['r'] == 6 and not '高级资深干员' in left[i]):
#                 continue
#             if right[i][j]['r'] != 6 and '高级资深干员' in left[i]:
#                 continue
#             temp.append(right[i][j])
#         # print(left[i], temp)
#         rright.append(temp)
#         if temp:
#             d[left[i]] = temp
#     d = sorted(d.items(), key=lambda d:(d[1][-1]['r'], len(d[1])), reverse=True)
#     # print(d)
#     return ans, d
#     # sstr = ''
#     # m = 1
#     # for i in d:
#     #     for j in i[0]:
#     #         sstr += j + '，'
#     #     sstr = sstr[:-1] + '：'
#     #     n = 6
#     #     for j in i[1]:
#     #         sstr += j['n'] + '，'
#     #         n = min(n, j['r'])
#     #     sstr = sstr[:-1] + '\n'
#     #     m = max(m, n)
#     # print(sstr[:-1])
#     # print(m)
    
# # print(search_items('固源岩'))
# # print(search_stages('1-7'))
# # arkRecruit('1')