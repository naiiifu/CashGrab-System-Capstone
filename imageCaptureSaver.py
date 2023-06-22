import cv2 as cv
import os
import numpy as np

#from picamera import PiCamera
#from picamera.array import PiRGBArray
from picamera2 import Picamera2  
import time

imageCount = 69
WARM_UP_TIME = 0.25

camera = Picamera2()
#camera.resolution = (1920,1080)
#full_res=camera.sensor_resolution
#half_res=tuple([dim // 2 for dim in camera.sensor_resolution])
#still_config=camera.create_still_configuration(main={"size":(720,720),"format":"RGB888"}, raw={"size":full_res})
#camera.start_preview(Preview.QTGL, x=100, y=200, width=800, height=600,transform=Transform(hflip=1))
#camera.resolution =(1296,972)
#camera.resolution = (1296,972)
#camera.configure(still_config)
camera.start()

def CaptureImage():
	time.sleep(WARM_UP_TIME)
	array = camera.capture_array("main")
	array = np.array(array, dtype=np.uint8)
	array = cv.cvtColor(array, cv.COLOR_BGR2RGB)
	
	return array
    
if __name__ == '__main__':
	endLoop = False
	while not endLoop:
		frame = CaptureImage()
		cv.imshow("Frame", frame)
		
		key = cv.waitKey(0)
		
		print(key)
		
		if key == 99: #lowecase c
			cv.imwrite('dfake{}.png'.format(imageCount), frame)
			imageCount = imageCount + 1
		elif key == 27: #esc
			endLoop = True
		cv.destroyAllWindows()