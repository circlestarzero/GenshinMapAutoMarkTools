import os
import re
from fuzzywuzzy import process
from xpinyin import Pinyin
base_dir = os.path.dirname(os.path.abspath(__file__))
name_list=[]
def listname():
        global name_list
        if len(name_list):
                return name_list;
        file_name = os.listdir(r'{0}\data'.format(base_dir))
        for nm in file_name:
                name_list.append(re.sub(r'.txt','',nm))
        return name_list
def inputandfind():
        lst=listname()
        pin = Pinyin()
        pinlist=[]
        for i in lst:
                pinlist.append([re.sub('-','',pin.get_pinyin(i)),i])
        name=input('请输入名称:(输入lst获取上次参数)\n')
        if name=='lst':
                return (2,None)
        rs_0=process.extract(name, lst, limit=10)
        rs_1=process.extract(name, pinlist, limit=10)
        rs=[]
        cnt=0
        for rss in rs_0:
                if rss[1]>80:
                        rs.append((cnt,rss[0]))
                        cnt+=1
        flag=0
        for rss in rs_1:
                flag=1
                if rss[1]>80:
                        flag=0
                for i in rs:
                        if rss[0][1]==i[1]:
                                flag=1
                                break
                if flag==0:
                        rs.append((cnt,rss[0][1]))
                cnt+=1
        print(rs)
        if len(rs)>0:
                nid=int(input('请输入序号:\n'))
                if nid>=0 and nid <len(rs):
                        return (1,rs[int(nid)][1])
                else:
                        print('序号不在范围,请重新输入')
                        return (0,None)  
        else:
                print('无匹配结果')
                return (0,None)
def ThirdKeySort(e):
        return e[2]
def SearchName(name):
        lst=listname()
        pin = Pinyin()
        pinlist=[]
        for i in lst:
                pinlist.append([re.sub('-','',pin.get_pinyin(i)),i])
        rs_0=process.extract(name, lst, limit=10)
        rs_1=process.extract(name, pinlist, limit=10)
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
if __name__ == '__main__':
        print(SearchName('deny'))