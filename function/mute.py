def time_to_str(second: int) -> str:
    
    minute = 0
    hour = 0
    day = 0
    if (second >= 60):
        minute = second // 60
        second = second % 60
    if (minute >= 60):
        hour = minute // 60
        minute = minute % 60
    if (hour >= 24):
        day = hour // 24
        hour = hour % 24
    # print(day, hour, minute, second)
    sstr = ((str(day) + '天') if (day != 0) else '') + (
        (str(hour) + '小时') if (hour != 0) else '') + (
        (str(minute) + '分钟') if (minute != 0) else '') + (
        (str(second) + '秒') if (second != 0) else '')
    return sstr