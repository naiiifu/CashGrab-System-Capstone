import cv2 as cv
import numpy as np

import orbFeatures
import kmeans
import LPP

from joblib import load

import training

images = [
    "validation/20230516_151701.jpg",
    "validation/20230516_151707.jpg",
    "validation/20230516_151712.jpg",
    "validation/20230516_151719.jpg",
    "validation/20230516_151725.jpg",
    ]

def getCGK(image):
    descriptors = orbFeatures.getORBDescriptors(image)

    npDescriptors = np.float32(descriptors)

    (labels, centers) = kmeans.getKMeans(npDescriptors)

    (dim4, dim8) = LPP.getLLP(centers)

    return (dim4, dim8)

def formatData(dim4, dim8):
    #dataArray = np.column_stack((dim4, dim8))
    dataArray =  np.float32(dim8)
    data = dataArray.reshape(-1)

    return data

def setUp():
    global clf

    with open(training.decTreeFile, "rb") as treeFile:
        clf = load(treeFile)

def getValue(image):
    (dim4, dim8) = getCGK(image)
    formatted = formatData(dim4, dim8)

    global clf
    value = clf.predict([formatted])

    return value

if __name__ == "__main__":
    setUp()
    for path in images:
        image = cv.imread(path)
        value = getValue(image)
        print(value[0])
