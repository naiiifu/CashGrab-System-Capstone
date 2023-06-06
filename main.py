import siftFlann
import cv2 as cv
import json
import numpy as np
import csv

import cProfile
import re

import pstats, io
from pstats import SortKey

pr = cProfile.Profile()

INLIER_THRESHOLD = 5.0
HYPOTHESIS_CONFIDENCE = 0.995
MAX_ITERATIONS = int(2000)
VALIDATION_CONFIDENCE = 0.0

DOWNSCALE_RATIO = 4

sift = cv.SIFT_create()

def HomographyShow(im1, im2):
    kp1, desc1 = sift.detectAndCompute(im1, None)
    kp2, desc2 = sift.detectAndCompute(im2, None)

    indexParams = dict(algorithm=0, trees=5)
    searchParams = dict(checks=50)

    flann = cv.FlannBasedMatcher(indexParams, searchParams)

    matches = flann.knnMatch(desc1, desc2, k=2)

    goodMatches = []

    for (m, n) in matches:
        if m.distance < 0.7 * n.distance:
            goodMatches.append(m)
    
    if len(goodMatches) >= 7: # min matches needed for ransac to work
        srcPoints = np.float32([kp1[m.queryIdx].pt for m in goodMatches]).reshape(-1, 1, 2)
        destPoints = np.float32([kp2[m.trainIdx].pt for m in goodMatches]).reshape(-1, 1, 2)

        M, mask = cv.findHomography(srcPoints, destPoints, cv.RANSAC, ransacReprojThreshold = INLIER_THRESHOLD, maxIters = MAX_ITERATIONS, confidence=HYPOTHESIS_CONFIDENCE)
        matchesMask = mask.ravel().tolist()
        inliers = np.sum(matchesMask)

        mse = 0

        assert(len(mask) == len(goodMatches))

        # for i in range(0, len(mask)):
        #     if goodMatches and mask[i]:

        if(M is not None):
            (h,w,p) = im1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv.perspectiveTransform(pts,M)

            # im2 = cv.polylines(im2,[np.int32(dst)],True,255,3, cv.LINE_AA)

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
            singlePointColor = None,
            matchesMask = matchesMask, # draw only inliers
            flags = 2)
                
        # print("RANSAC matches: " + str(inliers) + " Matched Features: " + str(len(goodMatches)))

        img3 = cv.drawMatches(im1,kp1,im2,kp2,goodMatches,None,**draw_params)
        cv.imshow('gray',img3)
        cv.waitKey(0)

        return (inliers, len(goodMatches))

    return (0, len(goodMatches))

class RANSACResults:
    realValue: int
    testValue: int
    ransacCount: int
    matchCount:  int

if __name__ == "__main__":
    im2 = cv.imread("./val/PXL_20230302_062157815.jpg")
    im2 = siftFlann.downScale(im2, 2)

    validationSetJsonPath = "./raspiCamTrainingSet.json"

    jsonFile = open(validationSetJsonPath)
    jsonObj = json.load(jsonFile)

    validationSetJsonPath = "./raspiCamTrainingSet.json"
    testSetJsonPath = "./piValidation.json"

    validationFile = open(validationSetJsonPath)
    validationObj = json.load(validationFile)

    testFile = open(testSetJsonPath)
    testObj = json.load(testFile)

    inliers = []

    pr.enable()

    with open("__.csv", 'w') as file:
        writer = csv.writer(file, lineterminator="\n")

        writer.writerow(["RealValue", "TestValue", "RansacCount", "FlannMatchCount"])
        
        """
        for entry in validationObj:
            path = entry["path"]

            image = cv.imread(path)
            image = siftFlann.downScale(image, 4)

            inlierCount = HomographyShow(image, im2)
            inliers.append(inlierCount)
        """

        for test in testObj:
                frontData = RANSACResults()
                backData = RANSACResults()

                front = cv.imread(testObj[test]['front'])
                front = siftFlann.downScale(front, DOWNSCALE_RATIO)
                back = cv.imread(testObj[test]['back'])
                back = siftFlann.downScale(back, DOWNSCALE_RATIO)

                value = testObj[test]['value']

                frontData.testValue = value
                backData.testValue = value

                for val in validationObj:
                    image = cv.imread(val['path'])
                    image = siftFlann.downScale(image, DOWNSCALE_RATIO)
                    valValue = val['value']

                    frontData.realValue = valValue
                    backData.realValue = valValue

                    (ransacFront, flannFront) = HomographyShow(front, image)
                    (ransacBack, flannBack) = HomographyShow(back, image)

                    frontData.matchCount = flannFront
                    frontData.ransacCount = ransacFront

                    backData.matchCount = flannBack
                    backData.ransacCount = ransacBack

                    writer.writerow([frontData.realValue, frontData.testValue, frontData.ransacCount, frontData.matchCount])
                    writer.writerow([backData.realValue, backData.testValue, backData.ransacCount, backData.matchCount])

                    print(str(frontData.realValue) + " " + str(frontData.testValue) + " " + str(frontData.ransacCount) + " " + str(frontData.matchCount))
                    print(str(backData.realValue) + " " + str(backData.testValue) + " " + str(backData.ransacCount) + " " + str(backData.matchCount))
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())