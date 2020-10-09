
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

def atme(msg: str) -> bool:
    return(msg.find("349468958") != -1 or
           msg.find("魔法使") != -1 or
           msg.find("筱蓝") != -1 or
           msg.find("小蓝") != -1 or
           msg.find("蓝蓝") != -1 or
           msg.find("七曜") != -1 or
           msg.find("xl") != -1 or
           msg.find("lsl") != -1 or
           msg.find("1424912867") != -1)
