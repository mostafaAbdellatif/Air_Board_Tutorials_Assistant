import numpy as np
import cv2
from collections import deque

def detect_pen(frame) :
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    Upper_hsv = np.array([153,255,255])
    Lower_hsv = np.array([64,72,49])
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=1)
    return cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
def draw(frame,paintWindow,points):
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

lp=512;
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0
kernel = np.ones((5,5),np.uint8)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0
cap = cv2.VideoCapture(0)
bpoints = [deque(maxlen=lp*2)]
gpoints = [deque(maxlen=lp*2)]
rpoints = [deque(maxlen=lp*2)]
ypoints = [deque(maxlen=lp*2)]


# Here is code for Canvas setup
paintWindow = np.zeros((471,636,3)) + 255
paintWindow = cv2.rectangle(paintWindow, (40,1), (140,65), (0,0,0), 2)
cv2.putText(paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)


laser=0
colour='green'

no_screen = 0
im_path = "img" + str(no_screen) + ".jpeg"

while True:

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if laser ==1:
        paintWindow[:,:,:] = 255
    cnts,_ = detect_pen(frame)
    center = None
 

    if len(cnts) > 0:
    	
        cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
        if laser ==1:
            cv2.circle(paintWindow, (int(x), int(y)), int(5), (0, 0, 255), 2)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if colour=='blue':
            colorIndex = 0 # Blue
        elif colour=='green':
            colorIndex = 1 # Green
        elif colour=='red':
            colorIndex = 2 # Red
        else :
            colorIndex = 3 # Yellow

        # Now checking if the user wants to click on any button above the screen 
        if (center[1] <= 65) and (laser==0):
            
            if 40 <= center[0] <= 140: # Clear Button
                bpoints = [deque(maxlen=lp)]
                gpoints = [deque(maxlen=lp)]
                rpoints = [deque(maxlen=lp)]
                ypoints = [deque(maxlen=lp)]

                blue_index = 0
                green_index = 0
                red_index = 0
                yellow_index = 0

                paintWindow[67:,:,:] = 255

        elif laser==0 :
            if colorIndex == 0:
                bpoints[blue_index].appendleft(center)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(center)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(center)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(center)
    # Append the next deques when nothing is detected to avoid messing up
    elif laser==0:
        bpoints.append(deque(maxlen=lp))
        blue_index += 1
        gpoints.append(deque(maxlen=lp))
        green_index += 1
        rpoints.append(deque(maxlen=lp))
        red_index += 1
        ypoints.append(deque(maxlen=lp))
        yellow_index += 1

    # Draw lines of all the colors on the canvas and frame 
    if laser ==0:
        points = [bpoints, gpoints, rpoints, ypoints]
        draw(frame,paintWindow,points)

    # Show all the windows
    cv2.imshow("Tracking", frame)
    cv2.imshow("Paint", paintWindow)
    


	# If the 'q' key is pressed then stop the application 

    if cv2.waitKey(1) & 0xFF == ord("l"):
        laser= not laser
        bpoints = [deque(maxlen=lp)]
        gpoints = [deque(maxlen=lp)]
        rpoints = [deque(maxlen=lp)]
        ypoints = [deque(maxlen=lp)]        
        blue_index = 0
        green_index = 0
        red_index = 0
        yellow_index = 0
        paintWindow[67:,:,:] = 255
# If the 's' key is pressed then take screenshot 
    if cv2.waitKey(1) & 0xFF == ord("s"):
        cv2.imwrite(im_path, paintWindow)
        print("screen shot saved")
        no_screen += 1
        im_path = "img" + str(no_screen) + ".jpeg"
	
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()
