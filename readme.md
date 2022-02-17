# 使用说明
## 适配
- windows7以上 64位
- 原神1920x1080,1366x768,1280x720窗口
- 待更新渊下宫和鹤观
- English version is to be updated
## 如何使用
### release 中下载文件并解压，以管理员权限运行main.exe,存放地址不要有中文路径和空格，原神以支持的窗口分辨率运行，且要在前台
### 代码运行环境
- 配置python 3.7+opencv3.1~3.4(之后版本因为专利问题surf使用起来很麻烦)+opencv contrib 我用的是opencv-python3.4.2.17
- 安装项目中所需的其他库pyqt5,keyboard...
- 以管理员权限运行main.py
## 功能
- 搜索地图资源并标点
- 删除当前地图界面所有标点
- 删除鼠标所在标点并加入资源刷新队列
- 获取鼠标所在标点的提示信息(比如宝箱怎么开)
- 删除当前所在位置标点并加入资源刷新队列
- 标点删除后经过对应刷新时间后刷新
- ~~小地图追踪map_track.py(目前解算速度只有0.6s/次，准确度在非城镇还可以)~~
## 技术方案
- python+opencv+qt5  
- opencv surf-flannbasedmatch 匹配当前地图坐标     
- 使用文件缓存图片特征点加速  
- 坐标由[天理坐标系](https://github.com/GengGode/GenshinImpact_AutoTrack_DLL#%E5%A4%A9%E7%90%86%E5%9D%90%E6%A0%87%E6%A8%A1%E5%9E%8B)换算成大地图图片坐标
- 使用opencv TM_SQDIFF_NORME算法D模板匹配查找原神ui按钮
- win32api模拟键盘鼠标
- pyqt编写ui界面

## 地图数据
- 地图标点数据源自
[空荧酒馆原神地图](https://github.com/kongying-tavern/yuan-shen-map)
## 配置快捷键
- config.in中每行冒号后修改  
- 具体支持快捷键参考python keyboard
