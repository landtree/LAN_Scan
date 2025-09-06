from time import sleep
import time
from picamera2 import Picamera2
from gpiozero import Motor,OutputDevice, InputDevice
import os
from ftplib import FTP
from libcamera import controls
import configparser


#setup camera
cam = Picamera2()
camera_config = cam.create_still_configuration()
cam.configure(camera_config)
cam.set_controls({"AfMode": controls.AfModeEnum.Continous})
cam.start()

#set angle motor
cameraAngle = Motor(2,3)
angleEnable = OutputDevice(4)

#set table motor
table = Motor(17,27)
tableEnable = OutputDevice(22)

#set hallEffect endstop
tableEndstop = InputDevice(20)
cameraEndstop = InputDevice(21)
#setup config parser
config = configparser.ConfigParser()

#create FTP
ftp = FTP()

def importConfigs():
	config.read('values.ini')
	tableRotations = int(config['values']['tableRotations'])
	NumberOfAngles = int(config['values']['NumberofAngles'])
	piLocalDir = config['values']['localDir']
	serverHost = config['values']['serverHost']
	totalPictures = tableRotations * NumberOfAngles
	tableIncrementTimer = 6/tableRotations
	cameraIncrementTimer = 2.1/NumberOfAngles

	print("")
	print("*********************************************")
	print("Current Settings")
	print("Camera timer: " + str(cameraIncrementTimer))
	print("Table timer: " + str(tableIncrementTimer))
	print("Total images: " + str(totalPictures))
	if os.path.isdir(piLocalDir):
		os.chdir(piLocalDir)
	else:
		os.makedirs(piLocalDir)
		os.chdir(piLocalDir)		
	print("Working Directory: " + str(piLocalDir))
	print("*********************************************")
	print("")

	return tableRotations, NumberOfAngles, totalPictures, tableIncrementTimer,cameraIncrementTimer, serverHost, piLocalDir

def tablehoming():
	"""
	Start moving and assume forward and time when the endstop triggers,
	if the enstop triggers under X amount of time, the motor needs to flip direction.
	"""
	#start moviung forward slowly
	table.forward(0.25)
	#capture the start time.
	startTime = time.clock.gettime_ns()
	trackingTime = 1

	while tableEndstop.value() == True:
		#start to speed up
		table.forward(0.5)
		if (time.clock.gettime_ns() - startTime) < trackingTime and endstop.value() == False :
			#assume we are inbetween the two endstops and we went the wrong direction.
			#leave and start going the other direction.
			break
	
	#reverse direction for 2 seconds, this should be enough to clear the the endstop
	#to home in the correct direction
	table.forward(1)
	table.reverse()
	sleep(2)

	#start tracking for the new endstop
	while tableEndstop.value() == True:
		#start to speed up
		table.forward(0.5)
		table.reverse()
	
	#stop the table 
	table.stop()

	#confirm home position
	table.forward(1)
	sleep(1)
	table.stop()

	while tableEndstop.value() == True:
		#slow to fine tune
		table.forward(0.1)
		table.reverse()	

def cameraHoming():
	#check current endstop position, assume its at the bottom of the rack first
	if cameraEndstop.value() == False:
		return
	
	#camera needs to be lowered, go slow to prevent overshoot,
	#as it needs to be a bit more accurate for timing.

	while cameraEndstop.value() == True:
		cameraAngle.forward(.1)
		cameraAngle.reverse()

	


def startFTP(serverHost):
	#start the ftp server
	print("Attempting to connect to server")
	try:
		ftp.connect(serverHost, 2121)
	except:
		print("Failed to connect, closing...")
		exit()

	print("connected!")
	print("logging in with 'scan' ")
	ftp.login('scan','scanner')
	mod = ftp.getwelcome().replace("220","")
	print("")
	print(mod.strip())
	print("")
	print("continuing in 2 seconds...")
	sleep(2)
	print("")

def sendImages(totalImages, folder_path):
	print("Sending " + str(totalImages) + " images.")

	for i in range(totalImages):
		filename = 'image_{:04d}.jpg'.format(i)
		print("Sending: " + str(filename))  
		with open(filename,'rb') as image_file:
			ftp.storbinary('STOR {}'.format(filename), image_file)

	print("finished upload")

	print("removing dir and images...")
	for filename in os.listdir(folder_path):
		file_path = os.path.join(folder_path, filename)
		# Check if the path is a file (not a directory)
		if os.path.isfile(file_path):
			# Delete the file
			os.remove(file_path)
			print(f"Deleted: {file_path}")


def captureImages(totalRotations, totalAngles, tableTimer, cameraTimer, totalImages):
	currentImages = 0
	currentAngle = 1
	direction = False
	totalRotations = totalRotations +1
	
	def checkEndstop():
		pass

	def rotate(direction):
		nonlocal currentImages
		if direction == False:
			for i in range(totalRotations):
				table.forward(1)
				sleep(tableTimer)
				table.stop()
				print("Progress: " + str(currentImages) + "/" + str(totalImages) )
				filename = 'image_{:04d}.jpg'.format(currentImages)

				cam.capture_file(filename)

				currentImages += 1
		else:
			for i in range(totalRotations):
				table.forward(1)
				table.reverse()
				sleep(tableTimer)
				table.stop()
				print("Progress: " + str(currentImages) + "/" + str(totalImages) )
				filename = 'image_{:04d}.jpg'.format(currentImages)
				cam.capture_file(filename)
				currentImages += 1

	def changeAngle(direction):
		cameraAngle.forward(1)
		sleep(cameraTimer)
		cameraAngle.stop()
		direction = not direction
		return direction

	while currentImages < totalImages:
		print("Current direction: " + str(direction))
		rotate(direction)
		print("Current angle: " + str(currentAngle))

		if(currentAngle < totalAngles):
			changeAngle(direction)
			currentAngle += 1


def main():
	configValues = importConfigs()
	startFTP(configValues[5])

	print("starting capturing sequence...")
	captureImages(configValues[0],configValues[1],configValues[3],configValues[4],configValues[2])

	print("Finsihed sequence...")
	sendImages(configValues[2],configValues[6])

if __name__ == '__main__':
    main()
