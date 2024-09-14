from time import sleep
from picamera2 import Picamera2
from gpiozero import Motor,OutputDevice
import os
from ftplib import FTP
from libcamera import controls

#setup camera

cam = Picamera2()
camera_config = cam.create_still_configuration()
cam.configure(camera_config)
cam.controls.AnalogueGain = 0.2
cam.start()


cameraMot = Motor(2,3)
cameraEn = OutputDevice(4)

tableMot = Motor(17,27)
tableEn = OutputDevice(22)

#camera vars import from config later
numCamPos = 8
numPicRot = 25
numPicTotal = numCamPos * numPicRot
increment = 0
j = 0
tableincrementTimer = 6 / numPicRot
camincrementTimer = 2.1/numCamPos

def delete_files_in_folder(folder_path):
    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {file_path}")

#path to store temp photos
#then move into the dir before connecting
dirpath = '/home/scan/Pictures/'
os.chdir(dirpath)

#create ftp object 
ftp = FTP()

print("attempting to connect")
ftp.connect('192.168.50.4',2121)
print("logging in")
ftp.login('scan','scanner')
MOD = ftp.getwelcome().replace("220", "")
print("")
print(MOD.strip())
print("")
sleep(2)

#check to see if there are files on the server
#files = []
#ftp.dir(files.append)
#display all files
# for f in files:
#     print(f)

print("Camera move Timer:" + str(camincrementTimer))
print("table move Timer:" + str(tableincrementTimer))
print("total images:" + str(numPicTotal))
sleep(3)

cameraEn.on()
tableEn.on()

# with cam.controls as controls:
#     controls.AnalogueGain = 0.1
#     
print("Taking photo of backplate, remove any object in place...")
input("Press enter when object is removed")

cam.capture_file("background.jpg")
cam.capture_file("background.jpg")
cam.capture_file("background.jpg")
cam.capture_file("background.jpg")
filename = 'background.jpg'   
with open(filename,'rb') as image_file:
    ftp.storbinary('STOR {}'.format(filename), image_file)
print("background sent to host")
input("Press enter when object is in place")
# with cam.controls as controls:
#     controls.AnalogueGain = .3

#flushes buffer to establish proper gain
filename = 'image_{:04d}.jpg'.format(1)
cam.capture_file(filename)
cam.capture_file(filename)
cam.capture_file(filename)
cam.capture_file(filename)

def rotateTable():
    global j
    for i in range(numPicRot):
        tableMot.forward(1)
        sleep(tableincrementTimer)
        tableMot.stop()
        j += 1
        filename = 'image_{:04d}.jpg'.format(j)
        cam.capture_file(filename)

def moveCam():
    cameraMot.forward(1)
    sleep(camincrementTimer)
    cameraMot.stop()
    
while increment < numCamPos:
    increment+=1
    rotateTable()
    moveCam()
    print("Current angle:" + str(increment))

if increment == numCamPos:
    cameraEn.on()
    cameraMot.forward(1)
    cameraMot.reverse()
    sleep(2.2)
    cameraMot.stop()
    print("done")

#send the photos into the dir
for i in range(1,numCamPos * numPicRot):
    filename = 'image_{:04d}.jpg'.format(i)    
    with open(filename,'rb') as image_file:
        ftp.storbinary('STOR {}'.format(filename), image_file)

print("finished upload")


print("Removing transferred files")
# Call the function to delete files in the specified folder
delete_files_in_folder(dirpath)

sleep(15)

ftp.quit()
