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
        self.bpoints = [deque(maxlen=self.lp*2)]
        self.gpoints = [deque(maxlen=self.lp*2)]
        self.rpoints = [deque(maxlen=self.lp*2)]
        self.ypoints = [deque(maxlen=self.lp*2)]


        # Here is code for Canvas setup
        self.paintWindow = np.zeros((471,636,3)) + 255
        self.paintWindow = cv2.rectangle(self.paintWindow, (40,1), (140,65), (0,0,0), 2)
        #cv2.putText(self.paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
        #cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

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
        
    def draw(self,frame,paintWindow,points):
        for i in range(len(points)):
            for j in range(len(points[i])):
                for k in range(1, len(points[i][j])):
                    if points[i][j][k - 1] is None or points[i][j][k] is None:
                        continue
                    cv2.line(frame, points[i][j][k - 1], points[i][j][k], self.colors[i], self.thickness)
                    cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], self.colors[i], self.thickness)
        return frame , paintWindow
    def drawFrame(self,frame):
        frame = cv2.flip(frame, 1)
        if self.laser == 1:
            self.paintWindow[:,:,:] = 255
        cnts,_ = self.detect_pen(frame)
        center = None
        x, y = 0 , 0
        if len(cnts) > 0:
            
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
            if self.laser ==1:
                cv2.circle(self.paintWindow, (int(x), int(y)), int(5), (0, 0, 255), 2)
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

            # Now checking if the user wants to click on any button above the screen 
            if (center[1] <= 65) and (self.laser==0):
                
                if 40 <= center[0] <= 140: # Clear Button
                    self.bpoints = [deque(maxlen=self.lp)]
                    self.gpoints = [deque(maxlen=self.lp)]
                    self.rpoints = [deque(maxlen=self.lp)]
                    self.ypoints = [deque(maxlen=self.lp)]

                    self.blue_index = 0
                    self.green_index = 0
                    self.red_index = 0
                    self.yellow_index = 0

                    self.paintWindow[67:,:,:] = 255

            elif self.laser==0 :
                if colorIndex == 0:
                    self.bpoints[self.blue_index].appendleft(center)
                elif colorIndex == 1:
                    self.gpoints[self.green_index].appendleft(center)
                elif colorIndex == 2:
                    self.rpoints[self.red_index].appendleft(center)
                elif colorIndex == 3:
                    self.ypoints[self.yellow_index].appendleft(center)
        # Append the next deques when nothing is detected to avoid messing up
        elif self.laser==0:
            self.bpoints.append(deque(maxlen=self.lp))
            self.blue_index += 1
            self.gpoints.append(deque(maxlen=self.lp))
            self.green_index += 1
            self.rpoints.append(deque(maxlen=self.lp))
            self.red_index += 1
            self.ypoints.append(deque(maxlen=self.lp))
            self.yellow_index += 1

        # Draw lines of all the colors on the canvas and frame 
        if self.laser ==0:
            points = [self.bpoints, self.gpoints, self.rpoints, self.ypoints]
            frame , self.paintWindow = self.draw(frame,self.paintWindow,points)

        # retuen all the windows
        return frame , self.paintWindow , (x, y)

# controller = AirBoardController()
# cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
# while True :
#     ret, frame = cap.read()
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     frame , paintWindow = controller.drawFrame(frame)
#     cv2.imshow("Tracking",frame)
#     cv2.imshow("Paint", paintWindow)
# cap.release()
# cv2.destroyAllWindows()
# while True:

#     ret, frame = cap.read()
#     frame = cv2.flip(frame, 1)
#     if laser ==1:
#         paintWindow[:,:,:] = 255
#     cnts,_ = detect_pen(frame)
#     center = None
 

#     if len(cnts) > 0:
    	
#         cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
#         ((x, y), radius) = cv2.minEnclosingCircle(cnt)
#         cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
#         if laser ==1:
#             cv2.circle(paintWindow, (int(x), int(y)), int(5), (0, 0, 255), 2)
#         M = cv2.moments(cnt)
#         center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

#         if colour=='blue':
#             colorIndex = 0 # Blue
#         elif colour=='green':
#             colorIndex = 1 # Green
#         elif colour=='red':
#             colorIndex = 2 # Red
#         else :
#             colorIndex = 3 # Yellow

#         # Now checking if the user wants to click on any button above the screen 
#         if (center[1] <= 65) and (laser==0):
            
#             if 40 <= center[0] <= 140: # Clear Button
#                 bpoints = [deque(maxlen=lp)]
#                 gpoints = [deque(maxlen=lp)]
#                 rpoints = [deque(maxlen=lp)]
#                 ypoints = [deque(maxlen=lp)]

#                 blue_index = 0
#                 green_index = 0
#                 red_index = 0
#                 yellow_index = 0

#                 paintWindow[67:,:,:] = 255

#         elif laser==0 :
#             if colorIndex == 0:
#                 bpoints[blue_index].appendleft(center)
#             elif colorIndex == 1:
#                 gpoints[green_index].appendleft(center)
#             elif colorIndex == 2:
#                 rpoints[red_index].appendleft(center)
#             elif colorIndex == 3:
#                 ypoints[yellow_index].appendleft(center)
#     # Append the next deques when nothing is detected to avoid messing up
#     elif laser==0:
#         bpoints.append(deque(maxlen=lp))
#         blue_index += 1
#         gpoints.append(deque(maxlen=lp))
#         green_index += 1
#         rpoints.append(deque(maxlen=lp))
#         red_index += 1
#         ypoints.append(deque(maxlen=lp))
#         yellow_index += 1

#     # Draw lines of all the colors on the canvas and frame 
#     if laser ==0:
#         points = [bpoints, gpoints, rpoints, ypoints]
#         draw(frame,paintWindow,points)

#     # Show all the windows
#     cv2.imshow("Tracking", frame)
#     cv2.imshow("Paint", paintWindow)
    


# 	# If the 'q' key is pressed then stop the application 

#     if cv2.waitKey(1) & 0xFF == ord("l"):
#         laser= not laser
#         bpoints = [deque(maxlen=lp)]
#         gpoints = [deque(maxlen=lp)]
#         rpoints = [deque(maxlen=lp)]
#         ypoints = [deque(maxlen=lp)]        
#         blue_index = 0
#         green_index = 0
#         red_index = 0
#         yellow_index = 0
#         paintWindow[67:,:,:] = 255
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

    

# # Release the camera and all resources
# cap.release()
# cv2.destroyAllWindows()