import datetime

import xlrd
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
