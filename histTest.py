import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import json
import siftFlann
import csv


histSize = 16
histRange = (0, 256) # the upper boundary is exclusive

hist_w = 512
hist_h = 400

class HistMatchPair:
    def __init__(self, val, wei):
        self.value = val
        self.weight = wei

    value : int
    weight : float

def GetHistogram(img, combined=False):
    # bgr_planes = cv.split(img)
    # accumulate = False
    # b_hist = cv.calcHist(bgr_planes, [0], None, [histSize], histRange, accumulate=accumulate)
    # g_hist = cv.calcHist(bgr_planes, [1], None, [histSize], histRange, accumulate=accumulate)
    # r_hist = cv.calcHist(bgr_planes, [2], None, [histSize], histRange, accumulate=accumulate)
    # cv.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
    # cv.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
    # cv.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)

    hist = cv.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv.normalize(hist, hist).flatten()

    return hist

    if combined:
        return np.array([b_hist, g_hist, r_hist], dtype=np.float32)
    else:
        return (b_hist, g_hist, r_hist)


def GetHistogramImage(img):
    bgr_planes = cv.split(img)
    accumulate = False
    b_hist = cv.calcHist(bgr_planes, [0], None, [histSize], histRange, accumulate=accumulate)
    g_hist = cv.calcHist(bgr_planes, [1], None, [histSize], histRange, accumulate=accumulate)
    r_hist = cv.calcHist(bgr_planes, [2], None, [histSize], histRange, accumulate=accumulate)
    bin_w = int(round( hist_w/histSize ))
    histImage = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
    cv.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
    cv.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
    cv.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)

    return (b_hist, g_hist, r_hist, histImage)

def DisplayHist(img):
    (b_hist, g_hist, r_hist, histImage) = GetHistogramImage(img)

    bin_w = int(round( hist_w/histSize ))
    
    for i in range(1, histSize):
        cv.line(histImage, ( bin_w*(i-1), hist_h - int(b_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(b_hist[i]) ),
                ( 255, 0, 0), thickness=2)
        cv.line(histImage, ( bin_w*(i-1), hist_h - int(g_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(g_hist[i]) ),
                ( 0, 255, 0), thickness=2)
        cv.line(histImage, ( bin_w*(i-1), hist_h - int(r_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(r_hist[i]) ),
                ( 0, 0, 255), thickness=2)
    
    cv.imshow('Source image', siftFlann.downScale(img, 2))
    cv.imshow('calcHist Demo', histImage)
    cv.waitKey()

def CompareHists(im1, im2):
    im1Hist = GetHistogram(im1, True)
    im2Hist = GetHistogram(im2, True)

    res = cv.compareHist(im1Hist, im2Hist, cv.HISTCMP_BHATTACHARYYA)

    return res

class HistResults:
    realValue: int
    testValue: int
    weight: float

if __name__ == "__main__":
    validationSetJsonPath = "./raspiCamTrainingSet.json"
    testSetJsonPath = "./piValidation.json"

    validationFile = open(validationSetJsonPath)
    validationObj = json.load(validationFile)

    testFile = open(testSetJsonPath)
    testObj = json.load(testFile)

    with open("hist.csv", 'w') as file:
        writer = csv.writer(file, lineterminator="\n")

        # writer.writerow(["RealValue", "TestValues", "Weights"])

        for val in validationObj:
            frontData = HistResults()
            backData = HistResults()

            image = cv.imread(val['path'])
            valValue = val['value']

            # frontData.realValue = valValue
            # backData.realValue = valValue

            frontData = []
            backData = []

            for test in testObj:
                front = cv.imread(testObj[test]['front'])
                back = cv.imread(testObj[test]['back'])
                value = testObj[test]['value']

                # frontData.testValue = value
                # backData.testValue = value

                frontRes = CompareHists(front, image)
                backRes = CompareHists(back, image)

                frontEntry = HistMatchPair(value, frontRes)
                backEntry = HistMatchPair(value, backRes)

                frontData.append(frontEntry)
                frontData.append(backEntry)
                
                # frontData.weight = frontRes
                # backData.weight = backRes

                # writer.writerow([frontData.realValue, frontData.testValue, frontData.weight])

            n = len(frontData)
            for i in range(0, n - 1):
                for j in range (0, n - i - 1):
                    if frontData[j].weight > frontData[j+1].weight:
                        temp = frontData[j]
                        frontData[j] = frontData[j+1]
                        frontData[j+1] = temp

            frontValues = []
            weights = []

            for entry in frontData:
                frontValues.append(entry.value)
                weights.append(entry.weight)

            writer.writerow([valValue] + frontValues + weights)
        
        file.close()

