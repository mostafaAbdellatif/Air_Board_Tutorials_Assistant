import numpy as np
import cv2
from collections import deque

class AirBoardController():
    """docstring for AirBoardController"""
    def __init__(self):
        super(AirBoardController, self).__init__()
        self.lp=512;
        self.blue_index = 0
        self.green_index = 0
        self.red_index = 0
        self.yellow_index = 0
        self.kernel = np.ones((5,5),np.uint8)
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
        self.colorIndex = 0
        #cap = cv2.VideoCapture(1)

        # Here is code for Canvas setup
        self.paintWindow = np.zeros((471,636,3)) + 255
        self.paintWindow = cv2.rectangle(self.paintWindow, (40,1), (140,65), (0,0,0), 2)
        #cv2.putText(self.paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
        #cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)
        self.lastPoint = (None,None)
        self.laser = 1
        self.colour='green'
        self.thickness = 2
        
    def setLaser(self):
        self.laser = 0
    def releseLaser(self):
        print("not")
        self.laser = 1

    def detect_pen(self,frame) :
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        Upper_hsv = np.array([153,255,255])
        Lower_hsv = np.array([64,72,49])
        Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
        Mask = cv2.erode(Mask, self.kernel, iterations=1)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, self.kernel)
        Mask = cv2.dilate(Mask, self.kernel, iterations=1)
        return cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
    def draw(self,point):
        if self.colour == 'green':
            cv2.line(self.paintWindow,self.lastPoint ,(point[0], point[1]), self.colors[1], self.thickness)
        elif self.colour == 'red':
            cv2.line(self.paintWindow,self.lastPoint , (point[0], point[1]), self.colors[2], self.thickness)
        elif self.colour == 'blue':
            cv2.line(self.paintWindow,self.lastPoint , (point[0], point[1]), self.colors[0], self.thickness)
        else:
            cv2.line(self.paintWindow,self.lastPoint , (point[0], point[1]), self.colors[3], self.thickness)
        self.lastPoint = point

    def drawFrame(self,frame):
        frame = cv2.flip(frame, 1)
        cnts,_ = self.detect_pen(frame)
        center = None
        x, y = 0 , 0
        if len(cnts) > 0:
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            if self.laser ==1:
                cv2.circle(frame, (int(x), int(y)), int(5), (0, 0, 255), 2)
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            if self.colour=='blue':
                colorIndex = 0 # Blue
            elif self.colour=='green':
                colorIndex = 1 # Green
            elif self.colour=='red':
                colorIndex = 2 # Red
            else :
                colorIndex = 3 # Yellow

        # Draw lines of all the colors on the canvas and frame 
        if self.laser == 0:
            if self.lastPoint == (None,None):
                self.lastPoint = (int(x), int(y))
            self.draw((int(x), int(y)))
        else :
            self.lastPoint = (None,None)

        # return all the windows
        self.paintWindow = cv2.resize(self.paintWindow,(frame.shape[1],frame.shape[0]))
        ret, paintWindowMask = cv2.threshold(self.paintWindow[:,:,0], 0, 255, cv2.THRESH_BINARY)
        frame[np.where(paintWindowMask == 0)] = self.paintWindow[np.where(paintWindowMask == 0)]
        
        return frame , self.paintWindow , (x, y)
'''a = AirBoardController()
cap = cv2.VideoCapture(1)
while 1:
    ret,image = cap.read()
    frame , paintWindow , (x, y)=a.drawFrame(image)
    cv2.imshow("sd",frame)'''

