import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture('hexbug-20.mp4')

centroid = []

while True:

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    try:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    except:
        break

##    # create trackbars for color change
##    cv2.createTrackbar('H','mask',0,180,nothing)
##    cv2.createTrackbar('S','mask',0,255,nothing)
##    cv2.createTrackbar('V','mask',0,255,nothing)
##
##    # get current positions of four trackbars
##    h = cv2.getTrackbarPos('H','mask')
##    s = cv2.getTrackbarPos('S','mask')
##    v = cv2.getTrackbarPos('V','mask')
##    print h,s,v
##
##    hradius = 36
##    sradius = 51
##    vradius = 51
##
##    hmin = max(  0,h-hradius)
##    hmax = min(180,h+hradius)
##    smin = max(  0,s-sradius)
##    smax = min(255,s+sradius)
##    vmin = max(  0,v-vradius)
##    vmax = min(255,v+vradius)

    hmin = 0
    hmax = 45

    smin = 100
    smax = 200

    vmin = 100
    vmax = 200

    # define range of color in HSV
    lower = np.array([hmin,smin,vmin])
    upper = np.array([hmax,smax,vmax])

    # Threshold the HSV image to get only selected colors
    mask = cv2.inRange(hsv, lower, upper)
    #cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)

    ret,thresh = cv2.threshold(mask,127,255,0)
    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    #print contours
    if contours:
        cnt = contours[0]
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            centroid.append([cx,cy])

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

print centroid[:-1]

cap.release()
cv2.destroyAllWindows()
