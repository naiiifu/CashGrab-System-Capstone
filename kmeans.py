import cv2 as cv

def getKMeans(descriptors):
    # alter as needed. take from openCV sample code
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv.KMEANS_RANDOM_CENTERS

    compactness,labels,centers = cv.kmeans(descriptors,32,None,criteria,10,flags)

    return (labels, centers)