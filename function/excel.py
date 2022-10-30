import datetime
import time

import xlrd
import xlsxwriter
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain


def takeclass(elem):
    return elem['class']

async def readexcel(app, group):
    now = datetime.date.today()
    lit = []
    workbook = xlrd.open_workbook('./source/wugao.xls')
    print(workbook.sheet_names())

    for i in range(1, 5):
        sheet = workbook.sheet_by_index(i)
        nrows = sheet.nrows
        ncols = sheet.ncols
        for j in range(1, nrows):
            cell_A = sheet.cell(j, 4).value
            if not cell_A.isdigit():
                continue
            month = int(cell_A[:2])
            day = int(cell_A[2:])
            if month == now.month and day == now.day:
                cell = sheet.cell(j, 1).value
                if type(cell) == type(1.0):
                    cls = str(int(cell))
                elif type(cell) == type(1):
                    cls = str(cell)
                else:
                    cls = str(cell)
                dit = {'class': cls,
                       'name': sheet.cell(j, 0).value}
                lit.append(dit)
    if lit:
        lit.sort(key=takeclass)
        s = '今天学校里过生日的人有：'
        for i in lit:
            s += '\n%s班%s' % (i['class'], i['name'])
        s += '\n祝他们生日快乐！'
        await app.send_group_message(group, MessageChain([Plain(s)]))

async def packup(app, group):
    data = await app.get_member_list(group)
    workbook = xlsxwriter.Workbook("./data/" + str(group) + ".xlsx")  # 创建工作簿
    xlsxwriter.Workbook()
    worksheet1 = workbook.add_worksheet("sheet1")  # 创建子表
    worksheet1.activate()  # 激活表
    title = ['序号', 'qq号', 'qq昵称','加群时间','最后发言时间']  # 设置表头
    worksheet1.write_row('A1', title)  # 从A1单元格开始写入表头
    i = 2  # 从第二行开始写入数据
    for j in range(len(data)):
        jt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[j].join_timestamp))
        lst = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[j].last_speak_timestamp))
        insertData = [j + 1, str(data[j].id), data[j].name, jt, lst]
        row = 'A' + str(i)
        worksheet1.write_row(row, insertData)
        i += 1
    workbook.close()  # 关闭表