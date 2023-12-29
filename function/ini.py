import configparser
import pathlib


def write_in_ini(Localpath: str, section: str, key: str, value: str):
    if pathlib.Path(Localpath).exists() == False:
        open(Localpath, 'w')
    config = configparser.ConfigParser()
    config.read(Localpath)
    if ((section in config) == False):
        config.add_section(section)
    config.set(section, key, value)
    with open(Localpath, "w") as fp:
        config.write(fp)


def write_in_ini_list(Localpath: str, section: list[str], key: str, value: str):
    if pathlib.Path(Localpath).exists() == False:
        open(Localpath, 'w')
    config = configparser.ConfigParser()
    config.read(Localpath)
    for i in section:
        if ((i in config) == False):
            config.add_section(i)
        config.set(i, key, value)
    with open(Localpath, "w") as fp:
        config.write(fp)


def read_from_ini(Localpath: str, section: str, key: str, fallback: str):
    if pathlib.Path(Localpath).exists() == False:
        return fallback
    config = configparser.ConfigParser()
    config.read(Localpath)
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
