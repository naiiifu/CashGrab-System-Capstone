import cv2 as cv
import os
import json
import numpy as np

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

def getBillValue(inputFeatures, masterValues, masterFrontFeatures, masterBackFeatures):
    THRESHOLD = 0

    value = -1
    mostMatches = -1

    for i in range(len(masterFrontFeatures)):
        matches = compareFeatures(inputFeatures, masterFrontFeatures[i])

        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append([m])
        
        if len(goodMatches) >= THRESHOLD and len(goodMatches) > mostMatches:
            mostMatches = len(goodMatches)
            value = masterValues[i]
    
    for i in range(len(masterBackFeatures)):
        matches = compareFeatures(inputFeatures, masterBackFeatures[i])

        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append([m])
        
        if len(goodMatches) >= THRESHOLD and len(goodMatches) > mostMatches:
            mostMatches = len(goodMatches)
            value = masterValues[i]
 
    print("Features: " + str(mostMatches) + " cutting off at " + str(FEATURE_CUTOFF))
    if(mostMatches <FEATURE_CUTOFF):#cutoff
        return 0
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

    for entry in jsonObj:
        path = entry["path"]

        image = cv.imread(path)
        value = entry["value"]

        if(value == 0):
            continue

        # print(value)

        (keypoints, features) = getSIFTFeatures(image)
        detectedValue = getBillValue(features, values, frontFeatures, backFeatures)

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