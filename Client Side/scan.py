from ftplib import FTP
from time import sleep
from picamera2 import Picamera2
from libcamera import Transform
from gpiozero import Servo
from gpiozero.tools import sin_values

import os

#setup servo controls
#gpiozero uses BCM numbering
#arm = AngularServo(17, min_angle=-90, max_angle=90)
#tilt = AngularServo(10, min_angle=-90, max_angle=90)


#setup camera
cam = Picamera2()
camConfig = cam.create_still_configuration(transform=Transform(vflip=1))
cam.configure(camConfig)
cam.start()

#camera vars import from config later
numPic = 10

#path to store temp photos
#then move into the dir before connecting
dirpath = '/home/scan/Pictures/'
os.chdir(dirpath)
 

    
print("starting caputre")

for i in range(numPic):
    cam.start_and_capture_file('image%s.jpg' %i,0.5)
    print("snap")
    
#send the photos into the dir
for i in range(numPic):
    with open('image%s.jpg' %i,'rb') as image_file:
        ftp.storbinary('STOR image%s.jpg' %i, image_file)

print("finished upload")
sleep(15)

ftp.quit()
