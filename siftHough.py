import siftFlann as sift
import cv2 as cv
import json
import hough
import numpy as np

validationSetJsonPath = "./raspiCamTrainingSet.json"

confusionIndexTable = {0: 0, 5: 1, 10: 2, 20: 3, 50: 4, 100: 5}
confusionMatrix = np.zeros((6, 6), dtype=np.uint)

if __name__ == "__main__":
    (values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector) = sift.houghLoadValidationSet("./validation.json", 1)

    appendedFeatures = []

    for feature in frontFeatures:
        appendedFeatures.append(feature)
    for feature in backFeatures:
        appendedFeatures.append(feature)

    hough.SetUp(appendedFeatures)

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

        (keypoints, features) = sift.houghGetSIFTFeatures(image)
        detectedValue = hough.GetBillValue(keypoints, features, values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector)

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
