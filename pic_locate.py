import numpy
import cv2 as cv
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
import win32gui
import sys
import time
import win32api
import win32print
import win32con
import os
import keyboard
import win32com.client
import pythoncom
base_dir = os.path.dirname(os.path.abspath(__file__))
app = QApplication(sys.argv)
def second_key_sort(k):
    return k[1]
def cutscreen(hwnd):
        pix = QApplication.primaryScreen().grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = pix.width()
        height = pix.height()
        ptr = pix.bits()
        ptr.setsize(height * width * 4)
        img = numpy.frombuffer(ptr, numpy.uint8).reshape((height, width, 4))
        img1 = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        return img1
def GetWindowCorner(hwnd):
    screen = QApplication.primaryScreen()
    pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    rect = win32gui.GetWindowRect(hwnd)
    hDC = win32gui.GetDC(0)
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    pscale = w/win32api.GetSystemMetrics(0)
    xf = int(rect[2]/pscale)-pix.width()
    yf = int(rect[3]/pscale)-pix.height()
    return [xf,yf]
def clk(pos,hwnd):
    time.sleep(0.1)
    off_set=GetWindowCorner(hwnd)
    pos=(pos[0]+off_set[0],pos[1]+off_set[1])
    win32api.SetCursorPos(pos)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
global window_height
window_height=0
def GetWindowHeight():
    global window_height
    if window_height!=0:
        return window_height
    hwnd = win32gui.FindWindow('UnityWndClass', None)
    screen = QApplication.primaryScreen()
    pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    window_height=pix.height()
    return window_height
def LocatePic(target,picname):
    matchResult=[]
    template = cv.imread(r"{0}\pic_{1}p\{2}.png".format(base_dir,GetWindowHeight(),picname),0)
    theight, twidth = template.shape[:2]
    result = cv.matchTemplate(target,template,cv.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    temp_loc = min_loc
    if min_val<0.01:
        matchResult.append([int(min_loc[0]+twidth/2),int(min_loc[1]+theight/2)])
    loc = numpy.where(result<0.01)
    for other_loc in zip(*loc[::-1]):
        if (temp_loc[0]-other_loc[0])**2>25 or(temp_loc[1]-other_loc[1])**2>25 :
            if (other_loc[0]-min_loc[0])**2>25 or(other_loc[1]-min_loc[1])**2>25 :
                    temp_loc = other_loc
                    matchResult.append([int(other_loc[0]+twidth/2),int(other_loc[1]+theight/2)])
    matchResult.sort(key=second_key_sort) 
    return matchResult
def OpenMap(hwnd):
    if len(LocatePic(cutscreen(hwnd),'close_btn'))==0:
        keyboard.send('m')
        return 0
    return 1
def SetBtnON(hwnd):
    pos=LocatePic(cutscreen(hwnd),'off_btn')
    if len(pos):
        clk(pos[0],hwnd)
        return 0
    return 1
def SetBtnOFF(hwnd):
    pos=LocatePic(cutscreen(hwnd),'on_btn')
    print(pos)
    if len(pos):
        clk(pos[0],hwnd)
        return 0
    return 1
def ClickBtn(hwnd):
    pos=LocatePic(cutscreen(hwnd),'confirm_btn')
    if len(pos):
        clk(pos[0],hwnd)
        return 0
    return 1
def ClickDel(hwnd):
    pos=LocatePic(cutscreen(hwnd),'del')
    if len(pos):
        print(pos)
        clk(pos[0],hwnd)
        return 0
    return 1
def ClickMarkList(hwnd):
    pos=LocatePic(cutscreen(hwnd),'marklist0')
    pos1=LocatePic(cutscreen(hwnd),'marklist1')
    if len(pos):
        clk(pos[0],hwnd)
        print(pos)
        return 0
    if(len(pos1)):
        clk(pos1[0],hwnd)
        print(pos1)
        return 0
    return 1
def DeleteAllMark(hwnd,name):
    poslist=LocatePic(cutscreen(hwnd),name)
    t1=time.clock()
    while len(poslist):
        time.sleep(0.2)
        clk(poslist[0],hwnd)
        time.sleep(0.1)
        flag=0
        while flag==0:
            for i in range(5):
                if ClickDel(hwnd)==0:
                    flag=1
                    break
            if flag==0:
                for i in range(5):
                    if ClickMarkList(hwnd)==0:break
        time.sleep(0.2)
        poslist=LocatePic(cutscreen(hwnd),name)
        t2=time.clock()
        if(t2-t1>10): break
    return

def DeleteAllMarks(hwnd):
    for i in range(7):
        DeleteAllMark(hwnd, 'mark{0}'.format(i))
    return
if __name__ == '__main__':
    hwnd = win32gui.FindWindow('UnityWndClass', None)
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    DeleteAllMarks(hwnd)
    #for i in range(7):
        #DeleteAllMark(hwnd, 'mark{0}'.format(i))
    #t1=time.clock()
    #print(LocatePic(cutscreen(hwnd),'marklist0'))
    #t2=time.clock()
    #print(t2-t1)
    #OpenMap(hwnd)