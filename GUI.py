import sys,os
import time
import numpy as np
import cv2
import keyboard
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QFileDialog,QShortcut
from PyQt5.QtCore import QTimer, QTime, Qt, QDate, QDateTime , QPropertyAnimation , QEvent
from PyQt5.QtGui import QColor, QKeySequence,QPixmap,QImage , QKeyEvent 

#from Air_board import *
from PIL import Image 
from Air_board import *
from Detection_Model import *
#from SideWindow import *
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MyWindow(QMainWindow):
        def __init__(self):
                super(MyWindow, self).__init__()
                # this will hide the title bar
                #self.setWindowFlag(Qt.FramelessWindowHint)
                uic.loadUi(resource_path("UI.ui"), self)
                #self.setGeometry(0,0,1280,720)
                self.MenuShow = QShortcut(QKeySequence("M"),self)
                self.MenuShow.activated.connect(self.ShowMenu)
                #self.MenuHide = QShortcut(QKeySequence("H"),self)
                #self.MenuHide.activated.connect(lambda: SideWindow.HideMenu(self))
                self.setWindowTitle("Air board")
                self.cap = None
                # create a timer
                self.timer = QTimer()
                # set timer timeout callback function
                self.timer.timeout.connect(self.Stream_Webcam)
                # set control_bt callback clicked  function
                self.EnableCamera.clicked.connect(self.controlTimer)
                self.camera_screen.setScaledContents(True)
                
                self.AirBoard = AirBoardController()

                self.MenuVisable = False
                
                self.Hand_Detector = Hand_Detector((10, 350, 225, 500))
                self.init_ui()
        def ShowMenu(self):
            if self.MenuVisable == False:
                self.MenuVisable = True
                self.ThicknessSlider.visable = True
            else:
                self.MenuVisable = False
                self.ThicknessSlider.visable = False
        def init_ui(self):
                return
        def get_thickness(self,x):
            self.AirBoard.thickness = int(x*10)
        def get_color(self,x):
            self.AirBoard.colour = 'green' if x < 0.3 else 'red'
        def get_option(self,x,y):
            if y in range(20,50):
                thickness = x/self.camera_screen.width()
                self.get_thickness(thickness)
                self.ThicknessSlider.setValue(thickness*150)
            elif y in range(100,130):
                self.get_color(x/self.camera_screen.width())
        def Stream_Webcam(self):
                ret, image = self.cap.read()
                #image = cv2.flip(image, 1)
                Hand = self.Hand_Detector.detect(image)
                if Hand is not None:
                    cv2.imshow("screen", Hand)
                # convert image to RGB format
                frame, paintWindow , (x, y) = self.AirBoard.drawFrame(image)
                
                if self.MenuVisable == True :
                    if keyboard.is_pressed('z'):
                        self.get_option(x,y)
                else :
                    if keyboard.is_pressed('z'):
                        self.AirBoard.laser = 0
                    else:
                        self.AirBoard.laser = 1
                # convert frame to RGB format
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # get image infos
                height, width, channel = frame.shape
                step = channel * width
                # create QImage from image
                cv2.rectangle(frame, (self.Hand_Detector.left, self.Hand_Detector.top), (self.Hand_Detector.right, self.Hand_Detector.bottom), (0, 255, 0), 2)
                qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
                # show image in img_label
                self.camera_screen.setPixmap(QPixmap.fromImage(qImg))
        def controlTimer(self):
                # if timer is stopped
                if not self.timer.isActive():
                    # create video capture
                    self.cap = cv2.VideoCapture(0)
                    # start timer
                    self.timer.start(20)
                    # update control_bt text
                    self.EnableCamera.setText("Disable Camera")
                # if timer is started
                else:
                    # stop timer
                    self.timer.stop()
                    # release video capture
                    self.cap.release()
                    self.camera_screen.clear()
                    # update control_bt text
                    self.EnableCamera.setText("Enable Camera")

if __name__ == '__main__':

    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MyWindow()
    mainWindow.show()

    sys.exit(app.exec_())