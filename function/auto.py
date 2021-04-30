import asyncio
import os
import random
import time
from ctypes import *  # 获取屏幕上某个坐标的颜色

import pyautogui as pag
import win32api
import win32gui
import win32con
import win32com.client

from pymouse import PyMouse

mouse = PyMouse()


def get_color(x, y):
    gdi32 = windll.gdi32
    user32 = windll.user32
    hdc = user32.GetDC(None)  # 获取颜色值
    pixel = gdi32.GetPixel(hdc, x, y)  # 提取RGB值
    r = pixel & 0x0000ff
    g = (pixel & 0x00ff00) >> 8
    b = pixel >> 16
    print([r, g, b])
    return [r, g, b]


def get_mouse():
    screenWidth, screenHeight = pag.size()  # 获取屏幕的尺寸
    x, y = pag.position()  # 返回鼠标的坐标
    print("Screen size: (%s %s),  Position : (%s, %s)" %
          (screenWidth, screenHeight, x, y))  # 打印坐标
    return [x, y]


def click_button(xx, yy):
    x = random.randint(xx[0], yy[0])
    y = random.randint(xx[1], yy[1])
    time.sleep(1)
    mouse.click(x, y)  # 移动并且在(x,y)位置左击


def jjc():

    click_button([823, 840], [1014, 878])  # 点冒险
    while True:
        if get_color(912, 672) == [214, 223, 255] and get_color(1189, 765) == [247, 247, 247]:
            break
        time.sleep(1)
    click_button([912, 672], [1189, 765])  # 点jjc
    while True:
        if get_color(796, 337) == [255, 255, 255] and get_color(1507, 450) == [255, 255, 255]:
            break
        time.sleep(1)
    click_button([796, 337], [1507, 450])  # 点最前面的名次

    while True:
        if get_color(1304, 757) == [90, 182, 255] and get_color(1500, 801) == [90, 105, 156]:
            break
        time.sleep(1)
    click_button([1304, 757], [1500, 801])  # 点开始战斗
    time.sleep(30)
    while True:
        if get_color(917, 284) == [33, 101, 33]:  # 赢了
            if get_color(1262, 820) == [82, 170, 239] and get_color(1515, 871) == [247, 190, 148]:
                break
        elif get_color(656, 412) == [82, 125, 189]:  # 输了
            if get_color(1234, 809) == [99, 190, 255] and get_color(1482, 846) == [90, 166, 255]:
                break
        time.sleep(2)

    click_button([1262, 820], [1515, 871])  # 点结束
    time.sleep(5)

    while True:
        if get_color(820, 836) == [222, 255, 255] and get_color(1021, 885) == [181, 235, 255]:
            break
        time.sleep(1)
    click_button([820, 836], [1021, 885])  # 点冒险
    while True:
        if get_color(1249, 672) == [181, 182, 214] and get_color(1526, 767) == [247, 243, 255]:
            break
        time.sleep(1)
    click_button([1249, 672], [1526, 767])  # 点pjjc
    while True:
        if get_color(796, 337) == [255, 255, 255] and get_color(1507, 450) == [255, 255, 255]:
            break
        time.sleep(1)
    click_button([796, 337], [1507, 450])  # 点最前面的名次

    for i in range(3):
        while True:
            if get_color(1304, 757) == [90, 182, 255] and get_color(1500, 801) == [90, 105, 156]:
                break
            time.sleep(1)
        click_button([1304, 757], [1500, 801])  # 点开始战斗
    time.sleep(90)
    while True:
        if get_color(1234, 809) == [99, 190, 255] and get_color(1482, 846) == [90, 166, 255]:
            break
        time.sleep(2)
    click_button([1234, 809], [1482, 846])  # 点结束


def testmain():
    time.sleep(2)
    wdname = u'公主连结R - MuMu模拟器'
    hwnd = win32gui.FindWindow(0, wdname)
    if not hwnd:
        print("窗口找不到，请确认窗口句柄名称：【%s】" % wdname)
        exit()
    # 窗口显示最前面
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')

    win32gui.SetForegroundWindow(hwnd)

    jjc()

def open():
    dir = r'F:\\Program Files (x86)\\MuMu\\emulator\\nemu\\EmulatorShell\\NemuPlayer.exe'
    win32api.ShellExecute(0, 'open', dir, '', '', 0)
    time.sleep(30)  
    wdname = u'MuMu模拟器'
    hwnd = win32gui.FindWindow(0, wdname)
    if not hwnd:
        print("窗口找不到，请确认窗口句柄名称：【%s】" % wdname)
        exit()
    # 窗口显示最前面
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')

    win32gui.SetForegroundWindow(hwnd)

    while True:
        if get_color(458, 556) == [90, 102, 169]:
            break
        time.sleep(2)
    click_button([458, 556], [478, 576])  # 点pcr启动程序
    for i in range(20):
        click_button([300,200],[1400,800])
        time.sleep(0.5)
    time.sleep(10)
    for i in range(20):
        click_button([300,200],[1400,800])
        time.sleep(0.5)
    time.sleep(10)

open()
testmain()

try:
    while True:
        screenWidth, screenHeight = pag.size()  # 获取屏幕的尺寸
        print(screenWidth, screenHeight)
        x, y = pag.position()  # 获取当前鼠标的位置
        posStr = "Position:" + str(x).rjust(4)+','+str(y).rjust(4)
        print(posStr)
        get_color(x, y)
        time.sleep(0.05)
        os.system('cls')  # 清楚屏幕
except KeyboardInterrupt:
    print('end....')
