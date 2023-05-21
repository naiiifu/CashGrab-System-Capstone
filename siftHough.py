import siftFlann as sift
import cv2 as cv
import json

validationSetJsonPath = "./trainingSet.json"

if __name__ == "__main__":
    (values, frontFeatures, backFeatures) = sift.loadValidationSet("./validation.json", 1)

    jsonFile = open(validationSetJsonPath)
    jsonObj = json.load(jsonFile)

    correctValues = 0
    incorrectValues = 0

    for entry in jsonObj:
        path = entry["path"]

        if "/disc/" in path:
            continue

        if "/plexi/" in path:
            continue

        image = cv.imread(path)
        value = entry["value"]
        print(value)
        (keypoints, features) = sift.getSIFTFeatures(image)
        detectedValue = sift.getBillValue(features, values, frontFeatures, backFeatures)

        if detectedValue == value:
            correctValues = correctValues + 1
        else:
            incorrectValues = incorrectValues + 1
    
    print(correctValues)
    print(incorrectValues)
