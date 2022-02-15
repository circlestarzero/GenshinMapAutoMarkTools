import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import win32gui
import sys
import time
import win32api
import win32print
import win32con
import re
import pickle
import os
import keyboard
import _thread
import pic_locate
import show_info
MIN_MATCH_COUNT = 10
surf = cv.xfeatures2d.SURF_create()
surf.setUpright(True)
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 1)
search_params = dict(checks = 1)
flann = cv.FlannBasedMatcher(index_params, search_params)
base_dir = os.path.dirname(os.path.abspath(__file__))
app = QApplication(sys.argv)
def AddDeletePos(deletedPos):
        markedlist=[]
        markednamelist=set()
        with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'rb') as f: 
                        if os.path.getsize(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir)):
                                markedlist=pickle.load(f)
        for l in markedlist:
                        if (deletedPos[0]-l[0])**2+(deletedPos[1]-l[1])**2<500:
                                markednamelist.add(l[2])
        namelist=list(markednamelist)
        if len(markednamelist)==0:
                show_info.Show_Info('未添加该点,删除失败')
                return 0
        elif len(markednamelist)>1:
                selected_name=show_info.GetSelection_Space(namelist)
        else:
                selected_name=namelist[0]
        with open(r'{0}\cache\deletedlist.txt'.format(base_dir),'a',encoding='utf-8') as f:
                        f.write(str(deletedPos[0]))
                        f.write(' ')
                        f.write(str(deletedPos[1]))
                        f.write(' ')
                        f.write(str(time.time()))
                        f.write(' ')
                        f.write(selected_name)
                        f.write('\n')
                        return 1
        return 0
def GetMapPostion(kp2, des2):
        hwnd = win32gui.FindWindow('UnityWndClass', None)
        pix = QApplication.primaryScreen().grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = pix.width()
        height = pix.height()
        rect = win32gui.GetWindowRect(hwnd)
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        pscale = w/win32api.GetSystemMetrics(0)
        ptr = pix.bits()
        ptr.setsize(height * width * 4)
        img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        img1 = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
        kp1, des1 = surf.detectAndCompute(img1, None)
        matches = flann.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
                if m.distance < 0.7*n.distance:
                        good.append(m)
        if len(good) > MIN_MATCH_COUNT:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
                M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
                h, w = img1.shape
                pts = np.float32([[0, 0], [0, h-1], [w-1, h-1],[w-1, 0]]).reshape(-1, 1, 2)
                dst = cv.perspectiveTransform(pts, M)
                pos=[[dst[0][0][0],dst[0][0][1]],[dst[2][0][0],dst[2][0][1]]]
                return (1,pos)
        else:
                return (0,None)
def GetCenterPosition(kp2,des2):
        rs=GetMapPostion(kp2, des2)
        if rs[0]==0:
                return (0,None)
        else:
                rs=rs[1]
                CenterPos=[int((rs[0][0]+rs[1][0])/2.0),int((rs[0][1]+rs[1][1])/2.0)]
                st=AddDeletePos(CenterPos)
                return (st,CenterPos)
def clk(x, y):
        win32api.SetCursorPos((x, y))
        time.sleep(0.14)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.30)
def DeleteMark(hwnd):
        flag=0
        t1=time.clock()
        while flag==0:
                for i in range(5):
                        if pic_locate.ClickDel(hwnd)==0:
                                flag=1
                                break
                if flag==0:
                        for i in range(5):
                                if pic_locate.ClickMarkList(hwnd)==0:break
                if time.clock()-t1>2:break
        time.sleep(0.2)
def ClickAndDeleteMark(hwnd):
        if pic_locate.ClickDel(hwnd)==0:
                return
        if pic_locate.ClickMarkList(hwnd)==0:
                time.sleep(0.4)
                pic_locate.ClickDel(hwnd)
                return
        pos=win32api.GetCursorPos()
        time.sleep(0.14)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        DeleteMark(hwnd)
        win32api.SetCursorPos(pos)
def deletecenter(hwnd,c1):
        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        rect = win32gui.GetWindowRect(hwnd)
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        pscale = w/win32api.GetSystemMetrics(0)
        xf = int(rect[2]/pscale)-pix.width()
        yf = int(rect[3]/pscale)-pix.height()
        center=(xf+int(pix.width()/2),yf+int(pix.height()/2))
        win32gui.SetForegroundWindow(hwnd)
        '''
        for i in range(40):
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,100)
                time.sleep(0.001)
        '''
        clk(center[0], center[1])
        DeleteMark(hwnd)
        time.sleep(0.2)
        win32api.SetCursorPos(center)
        keyboard.send('m')
def GetCursorPostion(hwnd):
        screen = QApplication.primaryScreen()
        pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        rect = win32gui.GetWindowRect(hwnd)
        hDC = win32gui.GetDC(0)
        w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
        pscale = w/win32api.GetSystemMetrics(0)
        left_top = (int(rect[2]/pscale)-pix.width(),int(rect[3]/pscale)-pix.height())
        pos=win32api.GetCursorPos()
        pos=(pos[0]-left_top[0],pos[1]-left_top[1])
        return pos
def GetCursorInMapPostion(hwnd,kp2,des2,mousePos):
        mapPostion=GetMapPostion(kp2, des2)
        if(mapPostion[0]==0):
                return (0,None)
        else:
                screen = QApplication.primaryScreen()
                pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
                mapPostion=mapPostion[1]
                scale=(mapPostion[1][0]-mapPostion[0][0])/pix.width()
                mouseInMapPostion=(int(mousePos[0]*scale+mapPostion[0][0]),int(mousePos[1]*scale+mapPostion[0][1]))
                return mouseInMapPostion
def GetCursorInMapPostionAndDelete(hwnd,kp2,des2,mousePos):
        mapPostion=GetMapPostion(kp2, des2)
        if(mapPostion[0]==0):
                return (0,None)
        else:
                screen = QApplication.primaryScreen()
                pix = screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
                mapPostion=mapPostion[1]
                scale=(mapPostion[1][0]-mapPostion[0][0])/pix.width()
                mouseInMapPostion=(int(mousePos[0]*scale+mapPostion[0][0]),int(mousePos[1]*scale+mapPostion[0][1]))
                st=AddDeletePos(mouseInMapPostion)
                return (st,mouseInMapPostion)
def DeleteCenterMark(kp,des):
        global kp2
        kp2=kp
        global des2
        des2=des
        global surf
        surf = cv.xfeatures2d.SURF_create()
        surf.setUpright(True)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        global flann
        flann = cv.FlannBasedMatcher(index_params, search_params)
        hwnd = win32gui.FindWindow('UnityWndClass', None)
        if pic_locate.OpenMap(hwnd)==0:
                time.sleep(0.60)
        _thread.start_new_thread( deletecenter,(hwnd,0,))
        _thread.start_new_thread( GetCenterPosition,(kp2,des2,))
def DeleteMouseMark(kp,des):
        global kp2
        kp2=kp
        global des2
        des2=des
        global surf
        surf = cv.xfeatures2d.SURF_create()
        surf.setUpright(True)
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        global flann
        flann = cv.FlannBasedMatcher(index_params, search_params)
        hwnd = win32gui.FindWindow('UnityWndClass', None)
        mousePos=GetCursorPostion(hwnd)
        _thread.start_new_thread( ClickAndDeleteMark,(hwnd,))
        _thread.start_new_thread( GetCursorInMapPostionAndDelete,(hwnd,kp2,des2,mousePos,))
        #win32api.SetCursorPos(mousePos)
def GetRefreshTime():
        refresh_time={}
        with open(r'{0}\cache\resourses_refresh_time.txt'.format(base_dir),'r',encoding='utf-8') as f:
                rs=f.readlines()
                for i in rs:
                        search_result=re.search(r'^(.*?)[ ](-?\d+)$',i,flags=0)
                        refresh_time[search_result.group(1)]=int(search_result.group(2))
        return refresh_time
def DeleteOutOfRefreshTime():
        marked=[]
        with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'rb') as f: 
                if os.path.getsize(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir)):
                        marked=pickle.load(f) 
        marked=list(marked)
        marked.reverse() 
        deleted=[]
        with open(r'{0}\cache\deletedlist.txt'.format(base_dir),'r',encoding='utf-8') as f:
                fl=f.readlines()
                for l in fl:
                        search_result=re.search(r'^(-?[.0-9]+) (-?[.0-9]+) (-?[.0-9]+) (.*)$',l,flags=0)
                        deleted.append([int(search_result.group(1)),int(search_result.group(2)),float(search_result.group(3)),search_result.group(4)])
        refresh_time=GetRefreshTime()
        for i in marked:
                flag=0
                for j in deleted:
                        if flag:break
                        if j[3]!=i[2]:continue
                        if (i[0]-j[0])**2+(i[1]-j[1])**2>2500:continue
                        if refresh_time[i[2]]==-1:continue
                        if refresh_time[i[2]]*3600<time.time()-j[2]:
                                marked.remove(i)
                                flag=1
                                deleted.remove(j)
                                continue
                        if refresh_time[i[2]]==1:#树木刷新时间为5分钟
                                if 300<time.time()-j[2]:
                                        marked.remove(i)
                                        flag=1
                                        deleted.remove(j)
                        if refresh_time[i[2]]==0:#一直存在的资源
                                marked.remove(i)
                                flag=1
                                deleted.remove(j)
        marked.reverse()
        with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'wb') as f:  
                        pickle.dump(marked,f)
        with open(r'{0}\cache\deletedlist.txt'.format(base_dir),'w',encoding='utf-8') as f:
                for l in deleted:
                        f.write(str(l[0]))
                        f.write(' ')
                        f.write(str(l[1]))
                        f.write(' ')
                        f.write(str(l[2]))
                        f.write(' ')
                        f.write(str(l[3]))
                        f.write('\n')
def DeleteMulti(lst):
        temp=set(lst)
        return list(temp)
def GetMarkInfo(hwnd,kp2,des2):   
        pos=GetCursorInMapPostion(hwnd,kp2,des2,GetCursorPostion(hwnd))
        mouse_pos=win32api.GetCursorPos()
        markedlist=[]
        markednamelist=set()
        with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'rb') as f: 
                        if os.path.getsize(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir)):
                                markedlist=pickle.load(f)
        for l in markedlist:
                        if (pos[0]-l[0])**2+(pos[1]-l[1])**2<100:
                                markednamelist.add(l[2])
        namelist=list(markednamelist)
        if len(markednamelist)==0:
                show_info.Show_Info('未添加该点')
                return 0
        elif len(markednamelist)>1:
                selected_name=show_info.GetSelection_Space(namelist)
        else:
                selected_name=namelist[0]
        coorlist = []
        with open(r"{0}\data\{1}.txt".format(base_dir,selected_name),mode='r',encoding='utf8') as f:
                data=f.readlines()
        result_list=[]
        for dt in data:
                rs=re.search(r'([-0-9.]+).*?([-0-9.]+)',dt,flags=0)
                a=(float(rs.group(1))*0.390*1.5+1426,float(rs.group(2))*0.3911*1.5+3015)
                if (pos[0]-a[0])**2+(pos[1]-a[1])**2<400:
                        temp=re.search(r'popupContent": "(.*?)" },', dt)
                        result_list.append(temp.group(1))
        win32api.SetCursorPos(mouse_pos)
        result_list=DeleteMulti(result_list)
        if len(result_list)==0:
                show_info.Show_Info('未添加该点')
        elif len(result_list)==1:
                show_info.Show_Info(result_list[0])
        else:
                show_info.GetSelection_Space(result_list)
        return 0
if __name__=='__main__':
        '''
        with open(r'{0}\cache\kplist.bin'.format(base_dir), 'rb') as f:
                kplist = pickle.load(f)
        kp2 = []
        for kp in kplist:
                kp2.append(cv.KeyPoint(kp['pt'][0], kp['pt'][1],kp['size'], kp['angle'], kp['octave'], kp['class_id']))
        des2 = np.load(r'{0}\cache\des2.npy'.format(base_dir))
        hwnd = win32gui.FindWindow('UnityWndClass', None)
        t1=time.time()
        print(GetMapPostion(kp2,des2))
        print(time.time()-t1)
        '''
        #GetMarkInfo(hwnd,kp2,des2)
