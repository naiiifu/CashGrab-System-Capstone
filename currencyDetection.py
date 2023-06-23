import cv2 as cv
import numpy as np
import json

import csv

import cProfile
import pstats, io
from pstats import SortKey
pr = cProfile.Profile()

USE_MSE_ERROR = False
ERROR_THRESHOLD = 0
FEATURE_THRESHOLD = 35

DOWNSCALE_RATIO = 2

USE_COLOR_HIST_FILTERING = True
COLOR_HIST_CONSIDERATION = 5

# RANSAC params
INLIER_THRESHOLD = 5.0
HYPOTHESIS_CONFIDENCE = 0.995
MAX_ITERATIONS = int(10000)

sift = cv.SIFT_create()

global keyImages
global keyValues
global keyKeypoints
global keyDescriptors
global keyColorHists
global points

keyImages = []
keyValues = []
keyKeypoints = []
keyDescriptors = []
keyColorHists = []
points = []

def getMatchIndex():
    global latestMatchIndex
    return latestMatchIndex

def getAffineTransform():
    global latestAffineTransform
    return latestAffineTransform

def getReferenceImage(referenceIndex):
    global keyImages
    return keyImages[referenceIndex]

def getReferencePoints(referenceIndex):
    global points
    return points[referenceIndex]

def SetUp(validationSetPath):
    jsonFile = open(validationSetPath)
    jsonObj = json.load(jsonFile)

    for key in jsonObj:
        # front image
        keyValues.append(jsonObj[key]['value'])

        frontImage = cv.imread(jsonObj[key]['front'])
        keyColorHists.append(GetHistogram(frontImage))

        frontImage = DownScale(frontImage, DOWNSCALE_RATIO)
        keyImages.append(frontImage)

        (frontKp, frontDesc) = GetFeatures(frontImage)

        keyKeypoints.append(frontKp)
        keyDescriptors.append(frontDesc)

        frontPoint = jsonObj[key]['points']['front']
        for i in range(0, len(frontPoint)):
            frontPoint[i] = (frontPoint[i][0] / DOWNSCALE_RATIO, frontPoint[i][1] / DOWNSCALE_RATIO)

        points.append(frontPoint)

        # back image
        keyValues.append(jsonObj[key]['value'])

        backImage = cv.imread(jsonObj[key]['back'])
        keyColorHists.append(GetHistogram(backImage))

        backImage = DownScale(backImage, DOWNSCALE_RATIO)
        keyImages.append(backImage)

        (backKp, backDesc) = GetFeatures(backImage)

        keyKeypoints.append(backKp)
        keyDescriptors.append(backDesc)

        backPoint = jsonObj[key]['points']['back']
        
        for i in range(0, len(backPoint)):
            backPoint[i] = (backPoint[i][0] / DOWNSCALE_RATIO, backPoint[i][1] / DOWNSCALE_RATIO)

        points.append(backPoint)

def GetHistogram(img):
    hist = cv.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv.normalize(hist, hist).flatten()

    return hist

def GetBestColorHistMatches(image):
    class HistMatchPair:
        def __init__(self, val, wei):
            self.index = val
            self.weight = wei

        index : int
        weight : float
    
    imageHist = GetHistogram(image)

    entries = []

    for i in range(0, len(keyValues)):
        histCorelation = cv.compareHist(imageHist, keyColorHists[i], cv.HISTCMP_BHATTACHARYYA)
        histMatch = HistMatchPair(i, histCorelation)
        entries.append(histMatch)

    n = len(entries)
    for i in range(0, n - 1):
        for j in range (0, n - i - 1):
            if entries[j].weight > entries[j+1].weight:
                temp = entries[j]
                entries[j] = entries[j+1]
                entries[j+1] = temp

    matches = []

    for i in range(0, COLOR_HIST_CONSIDERATION):
        # ensure returend indicies are ordered by correlation
        matches.append(entries[COLOR_HIST_CONSIDERATION - i - 1].index)

    return matches

def GetFeatures(image):
    kp, desc = sift.detectAndCompute(image, None)
    return (kp, desc)

def DownScale(image, scale):
    targetDim = (int(image.shape[1] / scale), int(image.shape[0] / scale))
    resized = cv.resize(image, targetDim, interpolation = cv.INTER_AREA)

    return resized

def MatchFeatures(inputFeatures, keyFeatures):
    indexParams = dict(algorithm=0, trees=5)
    searchParams = dict(checks=50)

    flann = cv.FlannBasedMatcher(indexParams, searchParams)
    matches = flann.knnMatch(inputFeatures, keyFeatures, k=2)

    goodMatches = []

    for (m, n) in matches:
        if m.distance < 0.7 * n.distance:
            goodMatches.append(m)
    
    return goodMatches

def CreateAffineModel(matches, inuptKeypoints, keyKeypoints):
    if len(matches) < 7:
        return (None, None)

    srcPoints = np.float32([inuptKeypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    destPoints = np.float32([keyKeypoints[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    M, mask = cv.findHomography(srcPoints, destPoints, cv.RANSAC, ransacReprojThreshold = INLIER_THRESHOLD, maxIters = MAX_ITERATIONS, confidence=HYPOTHESIS_CONFIDENCE)
    
    if M is None:
        return (None, None)

    return (M, mask)

def GetMSE(transform, mask, inuptKeypoints, keyKeypoints):
    return float("inf")

def Detect(image):
    if USE_COLOR_HIST_FILTERING:
        strongestHistogramMatchIndicies = GetBestColorHistMatches(image)
    else:
        strongestHistogramMatchIndicies = []

        for i in range(0, len(keyValues)):
            strongestHistogramMatchIndicies.append(i)

    downscaledImage = DownScale(image, DOWNSCALE_RATIO)
    (keypoints, descriptors) = GetFeatures(downscaledImage)

    bestMatchValue = 0

    if USE_MSE_ERROR:
        bestMatchError = float("inf")
    else:
        bestMatchError = 0

    for matchIndex in strongestHistogramMatchIndicies:
        matches = MatchFeatures(descriptors, keyDescriptors[matchIndex])

        affineModel = CreateAffineModel(matches, keypoints, keyKeypoints[matchIndex])

        (transform, mask) = affineModel

        if transform is None or mask is None:
            continue

        if USE_MSE_ERROR:
            error = GetMSE(transform, mask, keypoints, keyKeypoints[matchIndex])

            if error < bestMatchError:
                bestMatchError = error
                bestMatchValue = keyValues[matchIndex]
        else:
            # inlier count
            matchesMask = mask.ravel().tolist()
            inliers = np.sum(matchesMask)
            
            if inliers > bestMatchError:
                global latestAffineTransform
                global latestMatchIndex

                bestMatchError = inliers
                bestMatchValue = keyValues[matchIndex]
                latestMatchIndex = matchIndex
                latestAffineTransform = transform
    
    if USE_MSE_ERROR and bestMatchError < ERROR_THRESHOLD:
        return (bestMatchValue, bestMatchError)

    if bestMatchError > FEATURE_THRESHOLD:
        return (bestMatchValue, bestMatchError)
    
    return (0, bestMatchError)

if __name__ == "__main__":
    keyPath = "./piValidation.json"
    # trainingPath = "./raspiCamTrainingSet.json"
    trainingPath = "./finalValCombined.json"

    pr.enable()

    SetUp(keyPath)

    with open("RANSAC_Impl.csv", 'w') as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["RealValue", "TestValue", "Error"])

        trainingFile = open(trainingPath)
        trainingJson = json.load(trainingFile)

        for entry in trainingJson:
            image = cv.imread(entry['path'])
            inputValue = entry['value']

            (value, error) = Detect(image)

            writer.writerow([inputValue, value, error])
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())