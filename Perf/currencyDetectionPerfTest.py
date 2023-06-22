import currencyDetection
import cv2 as cv
import json

import csv

import cProfile
import pstats, io
from pstats import SortKey
pr = cProfile.Profile()

if __name__ == "__main__":
    keyPath = "./piValidation.json"
    trainingPath = "./raspiCamTrainingSet.json"

    pr.enable()

    currencyDetection.SetUp(keyPath)

    with open("RANSAC_Impl.csv", 'w') as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["RealValue", "TestValue", "Error"])

        trainingFile = open(trainingPath)
        trainingJson = json.load(trainingFile)

        for entry in trainingJson:
            image = cv.imread(entry['path'])
            inputValue = entry['value']

            (value, error) = currencyDetection.Detect(image)

            writer.writerow([inputValue, value, error])
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())