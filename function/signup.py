
import datetime
from function.ini import read_from_ini, write_in_ini


def signup(id: int) -> str:
    date = (read_from_ini('data\\签到.ini', str(id), 'date', '1970-01-01'))
    date = datetime.date.fromisoformat(date)
    now = datetime.date.today()
    delta = now - date
    if(delta.days == 1):
        num = 1 + int(read_from_ini('data\\签到.ini', str(id), 'num', '0'))
    elif(delta.days == 0):
        sstr = "您今天已经签到过了！"
        return sstr
    else:
        num = 1
    write_in_ini('data\\签到.ini', str(id), 'num', str(num))
    write_in_ini('data\\签到.ini', str(id), 'date', str(now))
    sstr = "签到成功！当前连续签到"+str(num)+"天"
    return sstr
