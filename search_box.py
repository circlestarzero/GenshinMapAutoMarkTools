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
import get_search_data
base_dir = os.path.dirname(os.path.abspath(__file__))
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
        self.text_list.data = get_search_data.SearchName(cur_text)
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
        map_insert.oper((1,self.custom_edit.select_text), self.slider.value())
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
        app = QApplication(sys.argv)
        ex = MainWindow(hwnd)
        ex.show()
        sys.exit(app.exec_())