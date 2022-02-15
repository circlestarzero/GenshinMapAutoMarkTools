import os
import re
from math import ceil
base_dir = os.path.dirname(os.path.abspath(__file__))
def GetSelection(list_name):
    rs=''
    for i in list_name:
        rs+=str(i)
        rs=rs+' '
    rs.strip(' ')
    command = r'py {0}\delete_mark_ui.py {1}'.format(base_dir,rs)
    r = os.popen(command)
    output = r.readlines()
    return output[0].strip('\n')
def GetSelection_Space(list_name):
    rs=''
    for i in list_name:
        rs+=re.sub(' ',';',str(i))
        rs=rs+' ' 
    rs.strip(' ')
    command = r'py {0}\delete_mark_ui.py {1}'.format(base_dir,rs)
    r = os.popen(command)
    output = r.readlines()
    return output[0].strip('\n')
def TurnListToStr(a):
    b=''
    for i in a:
        b+=str(i)
    return b
def Show_Info(info):
    list_info=list(info)
    show_info=[]
    if len(list_info)>10:
        row=int(ceil(len(list_info)/10))
        print(row)
        for i in range(row):
            show_info.append(TurnListToStr(list_info[i*10:min((i+1)*10,len(list_info))]))
        GetSelection_Space(show_info)
    else:
        GetSelection_Space([info])
    
if __name__=='__main__':
    Show_Info('abcdefghijklmnopqrstuvwxyz')