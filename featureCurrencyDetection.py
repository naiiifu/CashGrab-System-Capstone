import cv2 as cv
import json
import csv
import siftFlann



DOWNSCALE_RATIO = 4

def checkImg(image,values, frontFeatures, backFeatures):
    
    #image = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
    
    image = siftFlann.downScale(image, DOWNSCALE_RATIO)

    (keypoints, descriptors) = siftFlann.getSIFTFeatures(image)

    value = siftFlann.getBillValue(descriptors, values, frontFeatures, backFeatures)
    print(value)
    
  
if __name__ == '__main__':
    masterFolder = "./validation.json"
    (values, frontFeatures, backFeatures) = siftFlann.loadValidationSet(masterFolder, DOWNSCALE_RATIO)
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cv.imshow("Frame", frame)

    while True:

        key = cv.waitKey(1)
        if key == 99:
            ret, frame = cap.read()
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            cv.imshow("Frame", frame)
        if key ==100:
            checkImg(frame,values, frontFeatures, backFeatures)
        if key == 27:
            break

    cap.release()
    cv.destroyAllWindows()
