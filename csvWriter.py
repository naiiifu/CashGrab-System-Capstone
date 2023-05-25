import csv

def Write(path, features, nextMostFeatures, actualValue, detectedValue, totalFeatures, confidence, dbFeatures):
    assert(len(features) == len(actualValue))
    assert(len(features) == len(detectedValue))
    
    with open(path, 'w') as file:
        writer = csv.writer(file, lineterminator="\n")

        writer.writerow(["Features", "Second Most Features", "Actual Value", "Detected Value", "Total Features", "Confidence", "Reference Bill Features"])

        for i in range (0, len(features)):
            writer.writerow([features[i],nextMostFeatures[i],actualValue[i],detectedValue[i], totalFeatures[i], confidence[i], dbFeatures[i]])
        
        file.close()