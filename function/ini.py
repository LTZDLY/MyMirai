import configparser
import os
import json


def write_in_ini(Localpath: str, section: str, key: str, value: str):
    if os.path.exists(Localpath) == False:
        open(Localpath, 'w')
    config = configparser.ConfigParser()
    config.readfp(open(Localpath))
    if ((section in config) == False):
        config.add_section(section)
    config.set(section, key, value)
    config.write(open(Localpath, 'w'))


def read_from_ini(Localpath: str, section: str, key: str, fallback: str):
    if os.path.exists(Localpath) == False:
        return fallback
    config = configparser.ConfigParser()
    config.readfp(open(Localpath))
    return config.get(section, key, fallback=fallback)


'''
sstr = time.strftime("%Y-%m-%d", time.localtime())
print (sstr)
a = datetime.date.today()
b = datetime.date(2020,9,11)
c=a-b
print(a,b,c.days)
s = "2020-09-12"
print (datetime.date.fromisoformat(s))
'''
