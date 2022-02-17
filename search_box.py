import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import win32gui
import win32print
import win32con
import win32api
import win32com.client
import map_insert
import sys
import re
import pickle
import os
import pythoncom
import fuzzywuzzy
import xpinyin
import time
import keyboard
base_dir = os.path.dirname(os.path.abspath(__file__))
name_list=[]
MIN_MATCH_COUNT = 10
surf = cv.xfeatures2d.SURF_create()
surf.setUpright(True)
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv.FlannBasedMatcher(index_params, search_params)
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
def cmpcenter(i):
        return (i[0]-i[2])**2+(i[1]-i[3])**2
def findplace(pname):
    coorlist = []
    with open(r"{0}\data\{1}.txt".format(base_dir,pname),mode='r',encoding='utf8') as f:
        data=f.readlines()
    for dt in data:
        rs=re.search(r'([-0-9.]+).*?([-0-9.]+)',dt,flags=0)
        a=(float(rs.group(1))*0.390*1.5+1426,float(rs.group(2))*0.3911*1.5+3015)
        coorlist.append(a)
    return coorlist
def second_key_sort(k):
    return k[1]
def cutscreen(hwnd):
        pix = QApplication.primaryScreen().grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = pix.width()
        height = pix.height()
        ptr = pix.bits()
        ptr.setsize(height * width * 4)
        img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
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
def clk_1(pos,hwnd):
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
    loc = np.where(result<0.01)
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
        clk_1(pos[0],hwnd)
        return 0
    return 1
def SetBtnOFF(hwnd):
    pos=LocatePic(cutscreen(hwnd),'on_btn')
    print(pos)
    if len(pos):
        clk_1(pos[0],hwnd)
        return 0
    return 1
def ClickBtn(hwnd):
    pos=LocatePic(cutscreen(hwnd),'confirm_btn')
    if len(pos):
        clk_1(pos[0],hwnd)
        return 0
    return 1
def ClickDel(hwnd):
    pos=LocatePic(cutscreen(hwnd),'del')
    if len(pos):
        print(pos)
        clk_1(pos[0],hwnd)
        return 0
    return 1
def ClickMarkList(hwnd):
    pos=LocatePic(cutscreen(hwnd),'marklist0')
    pos1=LocatePic(cutscreen(hwnd),'marklist1')
    if len(pos):
        clk_1(pos[0],hwnd)
        print(pos)
        return 0
    if(len(pos1)):
        clk_1(pos1[0],hwnd)
        print(pos1)
        return 0
    return 1
def DeleteAllMark(hwnd,name):
    poslist=LocatePic(cutscreen(hwnd),name)
    t1=time.clock()
    while len(poslist):
        time.sleep(0.2)
        clk_1(poslist[0],hwnd)
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
def clk(x,y):
        time.sleep(0.3)
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
def listname():
        global name_list
        if len(name_list):
                return name_list;
        file_name = os.listdir(r'{0}\data'.format(base_dir))
        for nm in file_name:
                name_list.append(re.sub(r'.txt','',nm))
        return name_list
def SearchName(name):
        lst=listname()
        pin = xpinyin.Pinyin()
        pinlist=[]
        for i in lst:
                pinlist.append([re.sub('-','',pin.get_pinyin(i)),i])
        rs_0=fuzzywuzzy.process.extract(name, lst, limit=10)
        rs_1=fuzzywuzzy.process.extract(name, pinlist, limit=10)
        rs=[]
        for rss in rs_0:
                rs.append([rss[1],rss[0]])
        flag=0
        for rss in rs_1:
                flag=0
                for i in rs:
                        if rss[0][1]==i[1]:
                                flag=1
                                break
                if flag==0:
                        rs.append([rss[1],rss[0][1]])
        rs.sort(reverse=True)
        rslist=[]
        cnt=0
        for i in rs:
                if i[1]=='deny1' or i[1]=='deny0':continue
                rslist.append(i[1])
                cnt+=1
                if cnt>=7:break
        return rslist
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
def oper(select_name,notecnt):
        global lastDeleteTime
        if time.time()-lastDeleteTime>300:
                DeleteOutOfRefreshTime()
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
                OpenMap(hwnd)
                for i in range(10):
                        if SetBtnON(hwnd)==0:break
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
                                                if ClickBtn (hwnd)==0:break
                                                time.sleep(0.03)
                for i in range(10):
                        if SetBtnOFF(hwnd)==0:break
                        time.sleep(0.1)
                with open(r'{0}\cache\cache_alreadymarked.bin'.format(base_dir), 'wb') as f:  
                        pickle.dump(lst1,f)
        return
class QSSLoader:
    def __init__(self):
        pass
    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()
class CustomEdit(QLineEdit):
    is_close = QtCore.pyqtSignal()
    set_val_flag = 0
    last_val = 1
    def __init__(self, parent, size=(50, 50, 400, 30), name='edit',drag=False, text_list=True, search=True, qss_file=''):
        super(CustomEdit, self).__init__(None, parent)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.w = size[2]
        self.h = size[3]
        self.setGeometry(*size)
        self.setObjectName(name)
        self.drag_flag = False
        if drag:
            self.setAcceptDrops(True)
            self.setDragEnabled(True)
        else:
            self.setAcceptDrops(False)
            self.setDragEnabled(False)
        self.p_text = "" 
        self.list_model = QtCore.QStringListModel()
        self.text_list = QListView(parent)
        self.text_list.setObjectName("list_%s" % name)
        self.text_list.setGeometry(size[0]+12, size[1]+size[3]+5, size[2], size[3])
        self.text_list.hide()
        self.text_list.data = []
        self.func = None
        self.text_list.clicked.connect(lambda: self.on_select_data(self.func))
        if search:
            self.textChanged.connect(self.on_search_data)
    def on_search_data(self):
        cur_text = self.text()
        list_text = ''
        cur_text=re.sub(r'\s','',cur_text)
        if cur_text !='':
            self.text_list.show()
        if cur_text =='':
            self.text_list.data=[]
            self.set_last_data()
            return
        self.text_list.data = SearchName(cur_text)
        self.list_model.setStringList(self.text_list.data)
        self.text_list.setModel(self.list_model)
        if self.text_list.data:
            self.resize_text_list()
        else:
            self.text_list.hide() 
    def resize_text_list(self):
        self.text_list.resize(self.w-24, self.h * 1.1* (len(self.text_list.data)))
    def fill_data(self, text_data_list):
        self.list_model.setStringList(text_data_list)
        self.text_list.setModel(self.list_model)
        self.text_list.data = text_data_list
        if text_data_list:
            self.text_list.data = text_data_list
            self.text_list.resize(self.w-24, self.h * 1.1* len(self.text_list.data)+20)
        else:
            self.setText('')
        self.text_list.hide()
    def on_select_data(self, func):
        text = ''
        idx = self.text_list.currentIndex()
        if self.text_list.data:
            text = self.text_list.data[idx.row()]
        self.select_text=text
        self.text_list.hide()
        self.is_close.emit()
        self.close()
        if func:
            func()
    edit_clicked = QtCore.pyqtSignal()
    def set_last_data(self):
        if len(self.text_list.data)==0:
                with open(r'{0}\cache\cache_lstdata.bin'.format(base_dir), 'rb') as f: 
                    if os.path.getsize(r'{0}\cache\cache_lstdata.bin'.format(base_dir)):
                            last_data=pickle.load(f)
                            last_data.reverse()
                            self.text_list.data=[]
                            for dt in last_data:
                                    self.text_list.data.append(dt[0])
                            if len(last_data):
                                self.last_val=last_data[0][1]
                            self.text_list.data=self.text_list.data[:6]
                            self.fill_data(self.text_list.data)
                            self.text_list.show()
                            self.edit_clicked.emit()
                            
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.set_val_flag+=1
            self.set_last_data()
            
class MainWindow(QWidget):
    def __init__(self,hwnd):
        super(MainWindow, self).__init__()
        self.w = 0
        self.h = 0
        self.init_ui(hwnd)  
        style_file = r'{0}\qss\search_box.qss'.format(base_dir)
        style_sheet = QSSLoader.read_qss_file(style_file)
        self.setStyleSheet(style_sheet)
    def init_ui(self,hwnd):
        self.custom_edit = CustomEdit(self, size=(0, 0, 400, 60), 
                name='custom_edit', search=True)
        self.custom_edit.is_close.connect(self.close_all)
        self.slider=QSlider(QtCore.Qt.Horizontal,self)
        self.numLable=QLabel('1',self)
        self.slider.setGeometry(44, 70, 280, 20)
        self.slider.setMaximum(20)
        self.slider.setMinimum(1)
        self.numLable.setGeometry(344, 65, 30, 30)
        self.slider.valueChanged.connect(self.SetNum)
        self.w=self.custom_edit.width()+10
        self.h=self.custom_edit.height()+5
        self.resize(self.w, self.h)
        self.SetPos(hwnd)
        self.custom_edit.textChanged.connect(self.reset_window_size)
        self.custom_edit.edit_clicked.connect(self.reset_window_size)
        self.custom_edit.edit_clicked.connect(self.set_val)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.8)
    def set_val(self):
        if self.custom_edit.set_val_flag==1 :
            self.slider.setValue(self.custom_edit.last_val)
            self.numLable.setText(str(self.slider.value()))
    def close_all(self):
        self.hide()
        with open(r'{0}\cache\cache_lstdata.bin'.format(base_dir), 'rb') as f: 
                if os.path.getsize(r'{0}\cache\cache_lstdata.bin'.format(base_dir)):
                        last_data=pickle.load(f)
                else:
                    last_data=[]
        last_data.append([self.custom_edit.select_text, self.slider.value()])
        with open(r'{0}\cache\cache_lstdata.bin'.format(base_dir), 'wb') as f:
                result=[]
                last_data.reverse()
                for i in range(len(last_data)):
                    flag=0
                    for j in range(i):
                        if last_data[i][0]==last_data[j][0]:
                            flag=1
                            break
                    if flag==0:
                        result.append(last_data[i])
                result.reverse()
                if len(result)>6:
                    result=result[:6]
                pickle.dump(result,f)
        oper((1,self.custom_edit.select_text), self.slider.value())
        self.close()
    def SetNum(self):
        self.numLable.setText(str(self.slider.value()))
    def reset_window_size(self):
        self.resize(self.w, 5+self.custom_edit.text_list.height()*(1-self.custom_edit.text_list.isHidden())+self.custom_edit.height())
    def SetPos(self,hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        hDC = win32gui.GetDC(0)
        pscale=win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)/win32api.GetSystemMetrics(0) 
        rect=[int(rect[0]/pscale),int(rect[1]/pscale),int(rect[2]/pscale),int(rect[3]/pscale)]
        xmid=int((rect[0]+rect[2])/2.0)
        screen = QApplication.primaryScreen()
        pix=screen.grabWindow(hwnd).toImage()
        rect[1]=int(rect[3]/pscale)-pix.height()
        xlength=rect[2]-rect[0]
        ylength=rect[3]-rect[1]
        print((int(xmid-self.width()/2.0),int(rect[1]+ylength*0.1*0.2)))
        self.move(int(xmid-self.width()/2.0),int(rect[1]+ylength*0.1*0.2))
        win32api.SetCursorPos((int(xmid-self.width()/2.0)+20,int(rect[1]+ylength*0.1*0.2)+30))
if __name__=='__main__':
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        hwnd = win32gui.FindWindow('UnityWndClass', None)
        win32gui.SetForegroundWindow(hwnd)
        ex = MainWindow(hwnd)
        ex.show()
        sys.exit(app.exec_())