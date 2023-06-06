import cv2 as cv
import os
import numpy as np

from picamera import PiCamera
from picamera.array import PiRGBArray

imageCount = 10

camera = PiCamera()
camera.resolution = (1920,1080)

def CaptureImage():
	rawCapture = PiRGBArray(camera)
	camera.capture(rawCapture, format="rgb")
	frame = rawCapture.array
	
	frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
	
	return frame
	
	
	# output = np.empty(camera.resolution, dtype=np.uint8)
	# camera.capture(output, "rgb")
	
	# return output
	
	
	# frame = np.empty((camera.resolution[0], camera.resolution[1], 3), dtype=np.uint8)
	# print(len(frame))
	# camera.capture(frame, "bgr")
	
	# return rawCapture

def DeglareImage(image):
	print("2")
	grey = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
	mask = cv.threshold(grey, 220, 255, cv.THRESH_BINARY)[1]
	mask = cv.blur(mask, (3,3))
	cv.imshow("mask", mask) 
	print("3")
	
	result = cv.inpaint(image, mask, 21, cv.INPAINT_TELEA)
	print("4")
	return result
    
if __name__ == '__main__':
	endLoop = False
	while not endLoop:
		frame = CaptureImage()
		print("1")
		# deglared = DeglareImage(frame)
		print("5")
		cv.imshow("Frame", frame)
		
		key = cv.waitKey(0)
		
		print(key)
		
		if key == 99:
			cv.imwrite('{}.png'.format(imageCount), frame)
			imageCount = imageCount + 1
		elif key == 27:
			endLoop = True
		cv.destroyAllWindows()
