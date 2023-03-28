import cv2 as cv
import json
import csv
import siftFlann
import matplotlib.pyplot as plt


DOWNSCALE_RATIO = 4

def validateSift(jsonFile):
    f = open(jsonFile)
    data = json.load(f)

    properMatches = 0
    improperMatches = 0

    masterFolder = "./validation.json"

    (values, frontFeatures, backFeatures) = siftFlann.loadValidationSet(masterFolder, DOWNSCALE_RATIO)

    for i in range(len(data)):
        if '{}'.format(i) in data:
            image = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
            image = siftFlann.downScale(image, DOWNSCALE_RATIO)

            (keypoints, descriptors) = siftFlann.getSIFTFeatures(image)

            value = siftFlann.getBillValue(descriptors, values, frontFeatures, backFeatures)

            if(data['{}'.format(i)]["value"] == value):
                properMatches = properMatches + 1
            else:
                improperMatches = improperMatches + 1
                cv.imshow(data['{}'.format(i)]['front'], image)

    for i in range(len(data)):
        if '{}'.format(i) in data:
            image = cv.imread(data['{}'.format(i)]['back'],cv.IMREAD_GRAYSCALE)
            image = siftFlann.downScale(image, DOWNSCALE_RATIO)

            (keypoints, descriptors) = siftFlann.getSIFTFeatures(image)

            value = siftFlann.getBillValue(descriptors, values, frontFeatures, backFeatures)

            if(data['{}'.format(i)]["value"] == value):
                properMatches = properMatches + 1
            else:
                improperMatches = improperMatches + 1
                cv.imshow(data['{}'.format(i)]['back'], image)
    
    print("proper matches: " + str(properMatches))
    print("improper matches: " + str(improperMatches))

if __name__ == '__main__':
    validateSift('_BACKUP_data.json')

    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()
