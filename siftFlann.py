import cv2 as cv
import os
import json
import numpy as np
import csvWriter
import specialFunctions

sift = cv.SIFT_create()
FLANN_INDEX_KDTREE = 1
FEATURE_CUTOFF = 10

index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)   # or pass empty dictionary

flann = cv.FlannBasedMatcher(index_params,search_params)

confusionIndexTable = {0: 0, 5: 1, 10: 2, 20: 3, 50: 4, 100: 5}
confusionMatrix = np.zeros((6, 6), dtype=np.uint)

def downScale(image, scale):
    targetDim = (int(image.shape[1] / scale), int(image.shape[0] / scale))
    resized = cv.resize(image, targetDim, interpolation = cv.INTER_AREA)

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
        frontImage = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
        backImage = cv.imread(data['{}'.format(i)]['back'],cv.IMREAD_GRAYSCALE)

        frontImage = downScale(frontImage, downscaleRatio)
        backImage = downScale(backImage, downscaleRatio)

        frontImages.append(frontImage)
        backImages.append(backImage)
        values.append(data['{}'.format(i)]['value'])

    frontFeatures = []
    backFeatures = []

    for i in range(len(frontImages)):
        (keypoints, descriptors) = getSIFTFeatures(frontImages[i])
        frontFeatures.append(descriptors)

    for i in range(len(backImages)):
        (keypoints, descriptors) = getSIFTFeatures(backImages[i])
        backFeatures.append(descriptors)

    return (values, frontFeatures, backFeatures)

def getBillValue(inputFeatures, masterValues, masterFrontFeatures, masterBackFeatures, featureCount = False):
    THRESHOLD = 0

    value = -1
    mostMatches = -1
    nextMostMatches = -1

    for i in range(len(masterFrontFeatures)):
        matches = compareFeatures(inputFeatures, masterFrontFeatures[i])

        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append([m])
                
        if len(goodMatches) <= mostMatches and len(goodMatches) > nextMostMatches:
            nextMostMatches = len(goodMatches)

        if len(goodMatches) >= THRESHOLD and len(goodMatches) > mostMatches:
            mostMatches = len(goodMatches)
            value = masterValues[i]
    
    for i in range(len(masterBackFeatures)):
        matches = compareFeatures(inputFeatures, masterBackFeatures[i])

        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append([m])
        
        if len(goodMatches) <= mostMatches and len(goodMatches) > nextMostMatches:
            nextMostMatches = len(goodMatches)

        if len(goodMatches) >= THRESHOLD and len(goodMatches) > mostMatches:
            mostMatches = len(goodMatches)
            value = masterValues[i]
 
    print("Features: " + str(mostMatches) + " cutting off at " + str(FEATURE_CUTOFF))
    if(mostMatches <FEATURE_CUTOFF):#cutoff
        # testing only to get an idea of how we can reject matches. can be removed later
        if featureCount:
            return (0, mostMatches, nextMostMatches)
        return 0
    if featureCount:
        return (value, mostMatches, nextMostMatches)
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

if __name__ == "__main__":
    validationSetJsonPath = "./raspiCamTrainingSet.json"

    (values, frontFeatures, backFeatures) = loadValidationSet("./validation.json", 1)

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

    for entry in jsonObj:
        path = entry["path"]

        image = cv.imread(path)
        value = entry["value"]

        # print(value)

        (keypoints, features) = getSIFTFeatures(image)
        (detectedValue, featureCount, nextMost) = getBillValue(features, values, frontFeatures, backFeatures, True)

        
        featureArray.append(featureCount)
        nextFeatureAray.append(nextMost)
        realValueArray.append(value)
        detectedValueArray.append(detectedValue)
        totalFeatures.append(len(features))
        
        p = 0.04 * 0.085 * 0.5 / 14
        k = featureCount
        n = len(features)
        prob = specialFunctions.ibeta(k, n-k-1, p)
        print(prob)

        confidence.append(0.01 / (0.01 + prob))

        detectedValueIndex = confusionIndexTable[detectedValue]
        realValueIndex = confusionIndexTable[value]
        confusionMatrix[detectedValueIndex][realValueIndex] = confusionMatrix[detectedValueIndex][realValueIndex] + 1

        if detectedValue == value:
            correctValues = correctValues + 1
        else:
            incorrectValues = incorrectValues + 1
    
    print(correctValues)
    print(incorrectValues)
    print(confusionMatrix)

    csvWriter.Write("SiftFlann.csv", featureArray, nextFeatureAray, realValueArray, detectedValueArray, totalFeatures, confidence)