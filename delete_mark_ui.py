from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
import win32api
import re
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
class QSSLoader:
    def __init__(self):
        pass
    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r',  encoding='UTF-8') as file:
            return file.read()
class CustomListView(QListView):
    is_close=QtCore.pyqtSignal()
    def __init__(self , parent ,data_list):
        super(CustomListView, self).__init__(parent)
        self.w = 350
        if len(data_list)<=8:
            self.h= len(data_list)*60+40
        else:
            self.h= 8*60+40
        self.setGeometry(0,0,self.w,self.h)
        self.data = data_list
        self.list_model = QtCore.QStringListModel()
        self.list_model.setStringList(self.data)
        self.clicked.connect(self.on_select_data)
        self.setModel(self.list_model)
        self.show()
    def on_select_data(self):
        text = ''
        idx = self.currentIndex()
        if self.data:
            text = self.data[idx.row()]
        self.select_text=text
        self.hide()
        self.is_close.emit()
class MainWindow(QWidget):
    def __init__(self,data_list):
        super(MainWindow, self).__init__()
        self.init_ui(data_list)  
        style_file = r'{0}\qss\delete_mark_ui.qss'.format(base_dir)
        style_sheet = QSSLoader.read_qss_file(style_file)
        self.setStyleSheet(style_sheet)
    def init_ui(self,data_list):
        self.list_view=CustomListView(self,data_list)
        self.w=self.list_view.width()+10
        self.h=self.list_view.height()+5
        self.resize(self.w, self.h)
        self.SetPos()
        self.list_view.is_close.connect(self.closeall)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.8)
    def SetPos(self):
        pos=win32api.GetCursorPos()
        self.move(pos[0],pos[1])
    def closeall(self):
        print(self.list_view.select_text)
        self.close()
def main():
    app = QApplication(sys.argv)
    show_list=[]
    for i in range(1,len(sys.argv)):
        show_list.append(re.sub(r';',' ',str(sys.argv[i])))
    ex = MainWindow(show_list)
    ex.show()
    sys.exit(app.exec_())
main()