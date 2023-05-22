import json
from json import JSONEncoder
import cv2 as cv
# import CGK_Detect as cgk
import os
import numpy as np

jsonOut = []
i = 0

outputTable = [0, 5, 10, 20, 50, 100]

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
    
def recEnterPath(path):

    for itemName in os.listdir(path):
            itemPath = os.path.join(path, itemName)
            # checking if it is a file
            if os.path.isfile(itemPath):
                getBillValue(itemPath)
            else:       
                recEnterPath(itemPath)

def getBillValue(path):
    image = cv.imread(path)

    # (dim4, dim8) = cgk.getCGK(image)

    cv.imshow(path, cv.resize(image, (1920, 1080), interpolation = cv.INTER_AREA))
    value = cv.waitKey(0)

    storeJson(path, 0, 0, outputTable[value - 48])
    cv.destroyAllWindows()

def storeJson(path, dim4, dim8, value):
    global jsonOut
    global i
    
    jsonOut.insert(i, {
        "path" : path,
        "dim4" : dim4,
        "dim8" : dim8,
        "value": value
    })
    i = i + 1

if __name__ == "__main__":
    trainingSetPath = "./val/trainingData/raspicamNoPlexi"
    recEnterPath(trainingSetPath)

    with open("raspiCamTrainingSet.json", "w") as outfile:
        outfile.write(json.dumps(jsonOut, indent=4, cls=NumpyArrayEncoder))