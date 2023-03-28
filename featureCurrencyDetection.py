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


    image = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
    image = siftFlann.downScale(image, DOWNSCALE_RATIO)

    (keypoints, descriptors) = siftFlann.getSIFTFeatures(image)

    value = siftFlann.getBillValue(descriptors, values, frontFeatures, backFeatures)

    if(data['{}'.format(i)]["value"] == value):
        properMatches = properMatches + 1
    else:
        improperMatches = improperMatches + 1
        cv.imshow(data['{}'.format(i)]['front'], image)

  
    
  
if __name__ == '__main__':


    if cv.waitKey(0) & 0xff == 27:
        cv.destroyAllWindows()
