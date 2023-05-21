import cv2 as cv
import numpy as np

orb = cv.ORB_create()

def getORBFeatures(image):
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return (keypoints, descriptors)

def getORBDescriptors(image):
    keypoints, descriptors = orb.detectAndCompute(image, None)
    return descriptors

if __name__ == "__main__":
    im = cv.imread("./val/PXL_20230302_062303342.jpg")

    descriptors = getORBDescriptors(im)

    npDescriptors = np.float32(descriptors)

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv.KMEANS_RANDOM_CENTERS

    compactness,labels,centers = cv.kmeans(npDescriptors,32,None,criteria,10,flags)

    {}
    print("")
