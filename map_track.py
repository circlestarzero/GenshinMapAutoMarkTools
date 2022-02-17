import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage
import win32gui
import sys
import time
MIN_MATCH_COUNT = 8
surf = cv.xfeatures2d.SURF_create()
surf.setUpright(True)
hwnd = win32gui.FindWindow('UnityWndClass', None)   
app = QApplication(sys.argv)
img2 = cv.imread('pic\GIMAP.png',0) # trainImage
kp2, des2 = surf.detectAndCompute(img2,None)
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv.FlannBasedMatcher(index_params, search_params)
while(1):
    screen = QApplication.primaryScreen()   
    pix=screen.grabWindow(hwnd).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    width = pix.width()
    height = pix.height()
    ptr = pix.bits()
    ptr.setsize(height * width * 4)
    img = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    img=cv.cvtColor(img,cv.COLOR_RGB2GRAY)
    img1=img[23:226,62:262]
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
        matchesMask = mask.ravel().tolist()
        h,w= img1.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv.perspectiveTransform(pts,M)
        pt=(dst[0][0][0]+dst[1][0][0]+dst[2][0][0]+dst[3][0][0])/4.0,(dst[0][0][1]+dst[1][0][1]+dst[2][0][1]+dst[3][0][1])/4.0
        try:
            with open(r"C:\Users\circlezhu\Documents\GenshinImpactMapTrack-master\GenshinImpactMapTrack\input.txt",mode='w') as f:
                f.write("{:.4f}".format((pt[0]-1426))),f.write(' '),f.write("{:.4f}".format((pt[1]-3015)))
                print((pt[0],pt[1]))
        except:
            print('error')
    '''
    (2153.1306074497043, 378.9373107097881)
    (x-1426)*(2/3)/0.390f=x1
    x=x1*0.390*1.5+1426
    (y-3015)*(2/3)/0.3911f=y1
    y=y1*0.3911*1.5+3015

    1.227
    1.195
    1.240
    1426,3015 -> (0,0)
    x-x0
    y-y0
    3.190583347758352
    3.058542413381123
    <-

    '''
