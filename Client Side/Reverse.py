from time import sleep
from gpiozero import Motor,OutputDevice

cameraMot = Motor(2,3)
cameraEn = OutputDevice(4)

cameraEn.on()
cameraMot.forward(1)
cameraMot.reverse()
sleep(.1)
cameraMot.stop()
print("done")