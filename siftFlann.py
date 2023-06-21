import cv2 as cv
import os
import json
import numpy as np
import csvWriter
import specialFunctions

import cProfile
import re

import pstats, io
from pstats import SortKey

import threading

pr = cProfile.Profile()

sift = cv.SIFT_create()
FLANN_INDEX_KDTREE = 1
FEATURE_CUTOFF = 1

index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary

flann = cv.FlannBasedMatcher(index_params,search_params)
# flann = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)

confusionIndexTable = {0: 0, 5: 1, 10: 2, 20: 3, 50: 4, 100: 5}
confusionMatrix = np.zeros((6, 6), dtype=np.uint)

def downScale(image, scale):
    targetDim = (int(image.shape[1] / scale), int(image.shape[0] / scale))
    resized = cv.resize(image, targetDim, interpolation = cv.INTER_AREA)

    # cv.imshow("", resized)
    # cv.waitKey(0)

    return resized

def getSIFTFeatures(image):
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return (keypoints, descriptors)

def houghGetSIFTFeatures(image):
    kp = sift.detect(image)
    (loc, dec) = sift.compute(image, kp)

    return (loc, dec)

def compareFeatures(inputFeatures, comparisonFeatures):
    matches = flann.knnMatch(inputFeatures,comparisonFeatures,k=2)
    
    return matches

def loadValidationSet(jsonFile, downscaleRatio):
    print(jsonFile)
    file = open(jsonFile)
    data = json.load(file)

    frontImages = []
    backImages = []
    values = []

    for i in range(1, len(data) + 1):
        frontImage = cv.imread(data['{}'.format(i)]['front'])
        frontSize = frontImage.shape
        frontCrop = frontSize[1] / 2
        frontCrop = int(frontCrop)
        frontImage = frontImage[0:frontCrop, 0:frontSize[0]]
        

        backImage = cv.imread(data['{}'.format(i)]['back'])
        backSize = backImage.shape
        backCrop = backSize[1] / 2
        backCrop = int(backCrop)
        backImage = backImage[0:backCrop, 0:backSize[0]]

        frontImage = downScale(frontImage, downscaleRatio)
        backImage = downScale(backImage, downscaleRatio)

        frontImages.append(frontImage)
        backImages.append(backImage)
        values.append(data['{}'.format(i)]['value'])

    frontFeatures = []
    backFeatures = []
    frontPositions = []
    backPositions = []

    for i in range(len(frontImages)):
        (keypoints, descriptors) = getSIFTFeatures(frontImages[i])
        frontFeatures.append(descriptors)
        frontPositions.append(keypoints)

    for i in range(len(backImages)):
        (keypoints, descriptors) = getSIFTFeatures(backImages[i])
        backFeatures.append(descriptors)
        backPositions.append(keypoints)

    return (values, frontFeatures, backFeatures, frontPositions, backPositions)

def getBillValue(inputKeypoints, inputFeatures, masterValues, masterFrontFeatures, masterBackFeatures, masterFrontPositions, masterBackPositions, featureCount = False):
# def getBillValue(inputFeatures, masterValues, masterFrontFeatures, masterBackFeatures, featureCount = False):
    global mostMatches
    global nextMostMatches
    global dbFeatures
    global value
    global matchesSet
    global otherFeatures
    
    value = -1
    mostMatches = -1
    nextMostMatches = -1
    dbFeatures = -1
    matchesSet = []
    otherFeatures = []

    # lock = threading.Lock()

    global valuesArray
    global featureCountArray

    valuesArray = []
    featureCountArray = []

    def CompareImages(index, isFront, answerIndex):
        global mostMatches
        global nextMostMatches
        global dbFeatures
        global value
        global matchesSet
        global otherFeatures

        global valuesArray
        global featureCountArray

        if isFront:
            matchSet = masterFrontFeatures[index]
            # positionSet = masterFrontPositions[index]
        else:
            matchSet = masterBackFeatures[index]
            # positionSet = masterBackPositions[index]

        matches = compareFeatures(inputFeatures, matchSet)

        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append(m)

        inliers = len(goodMatches)

        valuesArray[answerIndex] = masterValues[index]
        featureCountArray[answerIndex] = inliers

        """
        lock.acquire() 
        if inliers <= mostMatches and inliers > nextMostMatches:
            nextMostMatches = len(goodMatches)

        if inliers >= FEATURE_CUTOFF and inliers > mostMatches:
            mostMatches = inliers
            value = masterValues[index]
            dbFeatures = len(matchSet)
            matchesSet = goodMatches
            otherFeatures = matchSet
        lock.release()
        """

    threadList = []

    answerIndex = 0

    for i in range(len(masterFrontFeatures)):
        valuesArray.append(0)
        featureCountArray.append(0)

        thread = threading.Thread(target = CompareImages, args=(i, True, answerIndex))
        thread.start()
        threadList.append(thread)
        answerIndex = answerIndex + 1
    
    for i in range(len(masterBackFeatures)):
        valuesArray.append(0)
        featureCountArray.append(0)

        thread = threading.Thread(target = CompareImages, args=(i, False, answerIndex))
        thread.start()
        threadList.append(thread)
        answerIndex = answerIndex + 1
    
    for thread in threadList:
        thread.join()

    for i in range(0, len(valuesArray)):
        if featureCountArray[i] >= FEATURE_CUTOFF and featureCountArray[i] > mostMatches:
            mostMatches = featureCountArray[i]
            value = valuesArray[i]
 
    print("Features: " + str(mostMatches) + " cutting off at " + str(FEATURE_CUTOFF))
    if(mostMatches <FEATURE_CUTOFF):#cutoff
        # testing only to get an idea of how we can reject matches. can be removed later
        if featureCount:
            return (0, mostMatches, nextMostMatches, dbFeatures, matchesSet, otherFeatures)
        return 0
    if featureCount:
        return (value, mostMatches, nextMostMatches, dbFeatures, matchesSet, otherFeatures)
    return value

def houghLoadValidationSet(jsonFile, downscaleRatio):
    file = open(jsonFile)
    data = json.load(file)

    frontImages = []
    backImages = []
    values = []

    for i in range(1, len(data) + 1):
        frontImage = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
        backImage = cv.imread(data['{}'.format(i)]['back'],cv.IMREAD_GRAYSCALE)

        frontImage = downScale(frontImage, downscaleRatio)
        backImage = downScale(backImage, downscaleRatio)

        frontImages.append(frontImage)
        backImages.append(backImage)
        values.append(data['{}'.format(i)]['value'])

    frontFeatures = []
    backFeatures = []
    frontFeatureVector = []
    backFeatureVector = []

    for i in range(len(frontImages)):
        (keypoints, descriptors) = houghGetSIFTFeatures(frontImages[i])
        frontFeatures.append(keypoints)
        frontFeatureVector.append(descriptors)

    for i in range(len(backImages)):
        (keypoints, descriptors) = houghGetSIFTFeatures(backImages[i])
        backFeatures.append(keypoints)
        backFeatureVector.append(descriptors)

    return (values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector)

def ToCVKeypoint(data):
    keypoint: cv.KeyPoint

    # {"angle": obj.angle, "class_id": obj.class_id, "octave": obj.octave, "pt": [obj.pt[0], obj.pt[1]], "response": obj.response, "size": obj.size}
    
    keypoint.angle = data["angle"]
    keypoint.class_id = data["class_id"]
    keypoint.octave = data["octave"]
    keypoint.pt = data["pt"]
    keypoint.response = data["response"]
    keypoint.size = data["size"]

    return keypoint

def setUp():
    global values, frontFeatures, backFeatures, frontPositions, backPositions
    values = []
    frontFeatures = []
    backFeatures = []
    frontPositions = []
    backPositions = []

    SERIALIZED_JSON_FILE = "serializedValidataion.json"

    file = open(SERIALIZED_JSON_FILE)
    data = json.load(file)

    for entry in data:
        values.append(entry["value"])
        frontFeatures.append(np.array(entry["frontFeatures"], dtype=np.float32))
        backFeatures.append(np.array(entry["backFeatures"], dtype=np.float32))
        frontPositions.append(np.array(entry["frontPositions"], dtype=np.float32))
        backPositions.append(np.array(entry["backPositions"], dtype=np.float32))

def detect(image, extra = False):
    global values, frontFeatures, backFeatures
    (keypoints, features) = getSIFTFeatures(image)

    detectedValue = getBillValue(keypoints, features, values, frontFeatures, backFeatures, frontPositions, backPositions, extra)

    return (features, detectedValue)

def PerfTest():
    validationSetJsonPath = "./raspiCamTrainingSet.json"

    jsonFile = open(validationSetJsonPath)
    jsonObj = json.load(jsonFile)

    correctValues = 0
    incorrectValues = 0

    setUp()
    
    pr.enable()
    
    for entry in jsonObj:
        path = entry["path"]

        image = cv.imread(path)
        value = entry["value"]
        
        detectedValue = detect(image)

        detectedValueIndex = confusionIndexTable[detectedValue]
        realValueIndex = confusionIndexTable[value]
        confusionMatrix[detectedValueIndex][realValueIndex] = confusionMatrix[detectedValueIndex][realValueIndex] + 1

        if detectedValue == value:
            correctValues = correctValues + 1
        else:
            incorrectValues = incorrectValues + 1
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

    print(correctValues)
    print(incorrectValues)
    print(confusionMatrix)

def AccuracyTest():
    validationSetJsonPath = "./raspiCamTrainingSet.json"

    (values, frontFeatures, backFeatures, frontPositions, backPositions) = loadValidationSet("./validation.json", 1)

    jsonFile = open(validationSetJsonPath)
    jsonObj = json.load(jsonFile)

    correctValues = 0
    incorrectValues = 0

    featureArray = []
    nextFeatureAray = []
    realValueArray = []
    detectedValueArray = []
    totalFeatures = []
    confidence = []
    dbFeaturesArray = []

    
    pr.enable()
    
    for entry in jsonObj:
        path = entry["path"]

        image = cv.imread(path)
        value = entry["value"]

        image = downScale(image, 2)
        (keypoints, features) = getSIFTFeatures(image)
        (detectedValue, featureCount, nextMost, dbFeatuers, matchesSet, otherFeatures) = getBillValue(keypoints, features, values, frontFeatures, backFeatures, frontPositions, backPositions, True)

        
        featureArray.append(featureCount)
        nextFeatureAray.append(nextMost)
        realValueArray.append(value)
        detectedValueArray.append(detectedValue)
        totalFeatures.append(len(features))
        dbFeaturesArray.append(dbFeatuers)
        
        p = 0.04 * 0.085 * 0.5
        k = featureCount
        n = len(features)
        prob = specialFunctions.ibeta(k, n-k+1, p)

        confidence.append(0.01 / (0.01 + prob))

        detectedValueIndex = confusionIndexTable[detectedValue]
        realValueIndex = confusionIndexTable[value]
        confusionMatrix[detectedValueIndex][realValueIndex] = confusionMatrix[detectedValueIndex][realValueIndex] + 1

        if detectedValue == value:
            correctValues = correctValues + 1
        else:
            incorrectValues = incorrectValues + 1
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

    print(correctValues)
    print(incorrectValues)
    print(confusionMatrix)

    csvWriter.Write("SiftFlann.csv", featureArray, nextFeatureAray, realValueArray, detectedValueArray, totalFeatures, confidence, dbFeaturesArray)

if __name__ == "__main__":
    AccuracyTest()