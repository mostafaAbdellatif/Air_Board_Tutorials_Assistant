# -------------------------------------------
# SEGMENT HAND REGION FROM A VIDEO SEQUENCE
# -------------------------------------------

# organize imports
import cv2
import numpy as np


class Hand_Detector():
    """docstring for Hand_Detector"""
    def __init__(self,roi):
        super(Hand_Detector, self).__init__()
        self.bg = None

        # initialize weight for running average
        self.aWeight = 0.5
        
        # region of interest (ROI) coordinates
        self.top, self.right, self.bottom, self.left = roi

        # initialize num of frames
        self.num_frames = -1

    # --------------------------------------------------
    # To find the running average over the background
    # --------------------------------------------------
    def run_avg(self,image):
        # initialize the background
        if self.bg is None:
            self.bg = image.copy().astype("float")
            return

        # compute weighted average, accumulate it and update the background
        cv2.accumulateWeighted(image, self.bg, self.aWeight)


    # ---------------------------------------------
    # To segment the region of hand in the image
    # ---------------------------------------------
    def segment(self,image, threshold=20):
        # find the absolute difference between background and current frame
        diff = cv2.absdiff(self.bg.astype("uint8"), image)

        # threshold the diff image so that we get the foreground
        thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]

        # get the contours in the thresholded image
        (cnts, _) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE

        # return None, if no contours detected
        if len(cnts) == 0:
            return
        else:
            # based on contour area, get the maximum contour which is the hand
            segmented = max(cnts, key=cv2.contourArea)
            # if segmented is not None:
            #   _, _, angle = cv2.fitEllipse(np.array(segmented))
            # 150-170 palm straight
            # 75-85
            # print(angle)
            return (thresholded, segmented)

    def detect(self,frame):
        # increment the number of frames
        self.num_frames += 1
        # get the ROI
        frame = cv2.flip(frame, 1)
        roi = frame[self.top:self.bottom, self.right:self.left]
        # convert the roi to grayscale and blur it
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if self.num_frames < 30:
            self.run_avg(gray)
        else:
            # segment the hand region
            hand = self.segment(gray)

            # check whether hand region is segmented
            if hand is not None:
                # if yes, unpack the thresholded image and
                # segmented region
                (thresholded, segmented) = hand

                # draw the segmented region and display the frame
                cv2.drawContours(frame.copy(), [segmented + (self.right, self.top)], -1, (0, 0, 255))
                if len(segmented) > 5:
                    _, _, angle = cv2.fitEllipse(np.array(segmented))
                    #print(angle)
                else:
                    angle = 0
                if angle > 149 and angle < 180:
                    return "show"
                elif angle > 40 and angle < 86:
                    return "close"
                else:
                    #print("none")
                    return  "none"