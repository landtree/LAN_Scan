from time import sleep
from gpiozero import Motor,OutputDevice

cameraMot = Motor(2,3)
cameraEn = OutputDevice(4)

tableMot = Motor(17,27)
tableEn = OutputDevice(22)

tableEn.on()
input("PRESS ENTER")

tableMot.forward(1)
sleep(.5)
tableMot.stop()