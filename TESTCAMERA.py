from picamera2 import Picamera2
import time

import numpy as np
import cv2 as cv

WARM_UP_TIME = 0.25

def Capture():
    picam2 = Picamera2()
    picam2.start()
    time.sleep(WARM_UP_TIME)
    array = picam2.capture_array("main")

    array = np.array(array, dtype=np.uint8)
    array = cv.cvtColor(array, cv.COLOR_BGR2RGB)

    return array

if __name__ == "__main__":
    array = Capture()

    cv.imshow(":)", array)
    cv.waitKey(0)