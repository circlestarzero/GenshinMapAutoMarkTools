import sys
import win32gui
import sys
import re
import os
import delete_mark
import keyboard
import win32com.client 
import pythoncom
import map_insert
import pic_locate
import delete_mark
base_dir = os.path.dirname(os.path.abspath(__file__))
def OpenSearchBox():
    st=os.system(r'python {0}\search_box.py'.format(base_dir))
def ImportConfig():
    config_list=[]
    with open('{0}\config.ini'.format(base_dir), 'r',  encoding='UTF-8') as f:
            temp=f.readlines()
            for i in range(5):
                gp=re.search(r'(:|：)\s*?(\S.*)\s*?', temp[i])
                if gp==None or len(gp.groups())<2:config_list.append('')
                else: config_list.append(gp.group(2))
    return config_list
if __name__=='__main__':
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    hwnd = win32gui.FindWindow('UnityWndClass', None)
    win32gui.SetForegroundWindow(hwnd)
    config=ImportConfig()
    if config[0]!='':
        keyboard.add_hotkey(config[0],OpenSearchBox,suppress = False)
    if config[1]!='':
        keyboard.add_hotkey(config[1],delete_mark.DeleteCenterMark,(map_insert.kp2,map_insert.des2),suppress = False)
    if config[2]!='':
        keyboard.add_hotkey(config[2],delete_mark.DeleteMouseMark,(map_insert.kp2,map_insert.des2),suppress = False)
    if config[3]!='':
        keyboard.add_hotkey(config[3],delete_mark.GetMarkInfo,(hwnd,map_insert.kp2,map_insert.des2),suppress = False)
    if config[4]!='':
        keyboard.add_hotkey(config[4],pic_locate.DeleteAllMarkIn_1080p,(hwnd,),suppress = False)
    keyboard.wait()