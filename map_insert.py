import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
import sys
import time
import win32gui
import win32api
import win32print
import win32con
import re
import pickle
import os
from get_search_data import inputandfind
import delete_mark
import keyboard
import win32com.client
import pythoncom
import pic_locate
MIN_MATCH_COUNT = 10
surf = cv.xfeatures2d.SURF_create()
surf.setUpright(True)
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 1)
search_params = dict(checks = 1)
flann = cv.FlannBasedMatcher(index_params, search_params)
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(r'{0}\cache\kplist.bin'.format(base_dir), 'rb') as f:  
    kplist=pickle.load(f)
kp2=[]
for kp in kplist:
    kp2.append(cv.KeyPoint(kp['pt'][0],kp['pt'][1],kp['size'],kp['angle'],kp['octave'],kp['class_id']))
des2=np.load(r'{0}\cache\des2.npy'.format(base_dir))
hwnd = win32gui.FindWindow('UnityWndClass', None)   
app = QApplication(sys.argv)
global lastDeleteTime
lastDeleteTime=0
def findplace(pname):
    coorlist = []
    with open(r"{0}\data\{1}.txt".format(base_dir,pname),mode='r',encoding='utf8') as f:
        data=f.readlines()
    for dt in data:
        rs=re.search(r'([-0-9.]+).*?([-0-9.]+)',dt,flags=0)
        a=(float(rs.group(1))*0.390*1.5+1426,float(rs.group(2))*0.3911*1.5+3015)
        coorlist.append(a)
    return coorlist
def clk(x,y):
        time.sleep(0.3)
        win32api.SetCursorPos((x, y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
def listname():
        file_name = os.listdir(r'{0}\data'.format(base_dir))
        print(file_name)
def cmpcenter(i):
        return (i[0]-i[2])**2+(i[1]-i[3])**2
def GetDeletedList():
    with open(r'{0}\cache\deletedlist.txt'.format(base_dir),'r',encoding='utf-8') as f:
        deletedlist=[]
        rawlist=f.readlines()
        for l in rawlist:
            rl=l.split(' ')
            deletedlist.append([int(rl[0]),int(rl[1]),float(rl[2])])
        return deletedlist
def oper(select_name,notecnt):
        global lastDeleteTime
        if time.time()-lastDeleteTime>300:
                delete_mark.DeleteOutOfRefreshTime()
                lastDeleteTime=time.time()
                print(lastDeleteTime)
        lst1=[]
        with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'rb') as f: 
                if os.path.getsize(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir)):
                        lst1=pickle.load(f)
        screen = QApplication.primaryScreen()
        pix=screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = pix.width()
        height = pix.height()
        rect = win32gui.GetWindowRect(hwnd)
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        pscale=w/win32api.GetSystemMetrics(0)
        xf=int(rect[2]/pscale)-width
        yf=int(rect[3]/pscale)-height
        ptr = pix.bits()
        ptr.setsize(height * width * 4)
        img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        img1=cv.cvtColor(img,cv.COLOR_RGB2GRAY)
        kp1, des1 = surf.detectAndCompute(img1,None)
        matches = flann.knnMatch(des1,des2,k=2)
        good = []
        for m,n in matches:
                if m.distance < 0.7*n.distance:
                        good.append(m)
        if len(good)>MIN_MATCH_COUNT:
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
                h,w= img1.shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv.perspectiveTransform(pts,M)
                xlength=dst[2][0][0]-dst[0][0][0]
                ylength=dst[2][0][1]-dst[0][0][1]
                scale=(xlength/img1.shape[1]+ylength/img1.shape[0])/2.0
                #win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                pythoncom.CoInitialize()
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.1)
                pic_locate.OpenMap(hwnd)
                for i in range(10):
                        if pic_locate.SetBtnON(hwnd)==0:break
                        time.sleep(0.2)
                ltt=findplace(select_name[1])
                lst=[]
                for l in ltt:
                        lst.append([l[0],l[1],(dst[2][0][0]+dst[0][0][0])/2.0,(dst[2][0][1]+dst[0][0][1])/2.0])
                lst.sort(key=cmpcenter)
                denylist=findplace('deny1')
                cnt=0
                for ls in lst:
                        x1,y1=ls[:2]
                        flag=0
                        #判断范围
                        for l in lst1:
                                if (x1-l[0])**2+(y1-l[1])**2<2000*scale*scale and select_name[1]==l[2]:
                                        flag=1
                                        break
                        
                        if flag==0:
                                for l in denylist:
                                        if (x1-l[0])**2+(y1-l[1])**2<2500*scale*scale:
                                                flag=1
                                                break
                                b1=(x1-dst[0][0][0])/scale<350/1920.0*img1.shape[1] and (y1-dst[0][0][1])/scale<200/1080.0*img1.shape[0]
                                b2=(x1-dst[0][0][0])/scale>1347/1920.0*img1.shape[1] and (y1-dst[0][0][1])/scale<82/1080.0*img1.shape[0]
                                b3=(x1-dst[0][0][0])/scale<140/1920.0*img1.shape[1] and (y1-dst[0][0][1])/scale>960/1080.0*img1.shape[0]
                                b4=(x1-dst[0][0][0])/scale>1667/1920.0*img1.shape[1] and (y1-dst[0][0][1])/scale>967/1080.0*img1.shape[0]
                                if b1 or b2 or b3 or b4:
                                        flag=1
                                b5=x1>dst[0][0][0] and x1<dst[2][0][0] and y1>dst[0][0][1] and y1<dst[2][0][1]
                                if b5 and flag==0 and cnt<notecnt:
                                        lst1.append([ls[0],ls[1],select_name[1]])
                                        cnt+=1       
                                        xps=int((x1-dst[0][0][0])/scale+xf)
                                        yps=int((y1-dst[0][0][1])/scale+yf)
                                        clk(xps,yps)
                                        for i in range(20):
                                                if pic_locate.ClickBtn (hwnd)==0:break
                                                time.sleep(0.03)
                for i in range(10):
                        if pic_locate.SetBtnOFF(hwnd)==0:break
                        time.sleep(0.1)
                with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'wb') as f:  
                        pickle.dump(lst1,f)
        return
def notecnt(select_name):
        flag=0
        while flag==0:
                cnt=input('请输入标点个数:\n')
                cnt=int(cnt)
                lst=findplace(select_name[1])
                if cnt>len(lst) or cnt<= 0:
                        print('范围错误')
                        return -1
                else:
                        flag=1
        return cnt
def MarkMap(kp2,des2):
        global lastDeleteTime
        if time.time()-lastDeleteTime>300:
                delete_mark.DeleteOutOfRefreshTime()
                lastDeleteTime=time.time()
                print('hello')
                print(lastDeleteTime)
        pythoncom.CoInitialize()
        mainhwnd = win32gui.FindWindow('ConsoleWindowClass', None)  
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(mainhwnd)
        bdir=os.path.dirname(os.path.abspath(__file__))
        with open(r'{0}\cache\cache_lstdata.bin'.format(bdir), 'rb') as f: 
                if os.path.getsize(r'{0}\cache\cache_lstdata.bin'.format(bdir)):
                        lstdata=pickle.load(f)
                else:
                        lstdata=[0,0]
        select_name=inputandfind()
        while select_name[0]==0:
                select_name=inputandfind()
        if select_name[0]==2:
                print(lstdata)
                if lstdata[1]!=0:
                        oper(lstdata[0],lstdata[1])
                else:
                        print('上次未输入')
        else:
                cct=notecnt(select_name)
                if cct==-1:
                        return
                oper(select_name,cct)
                lstdata=[select_name,cct]
                with open(r'{0}\cache\cache_lstdata.bin'.format(bdir), 'wb') as f:  
                        pickle.dump(lstdata,f)
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)
if __name__=='__main__':
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(hwnd)
        keyboard.add_hotkey('ctrl+m',MarkMap,(kp2,des2))
        keyboard.add_hotkey('ctrl+p',delete_mark.DeleteCenterMark,(kp2,des2))
        keyboard.add_hotkey('ctrl+d',delete_mark.DeleteMouseMark,(kp2,des2))
        keyboard.wait()