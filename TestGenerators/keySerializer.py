import json
import cv2 as cv
import siftFlann
import trainingSetGeneration

def LoadSerializeReferenceSet(serializeDataJson):
    values, frontFeatures, backFeatures, frontPositions, backPositions = []
    
    file = open(serializeDataJson)
    data = json.load(file)

    for entry in data:
        values.append(entry['value'])
        frontFeatures.append(entry['frontFeatures'])
        backFeatures.append(entry['backFeatures'])
        frontPositions.append(entry['frontPositions'])
        backPositions.append(entry['backPositions'])

    return (values, frontFeatures, backFeatures, frontPositions, backPositions)

if __name__ == "__main__":
    VALIDATION_SET = "validation.json"
    OUTPUT_FILE = "serializedValidataion.json"

    file = open(VALIDATION_SET)
    data = json.load(file)

    frontImages = []
    backImages = []
    values = []

    for i in range(1, len(data) + 1):
        frontImage = cv.imread(data['{}'.format(i)]['front'])
        backImage = cv.imread(data['{}'.format(i)]['back'])

        frontImages.append(frontImage)
        backImages.append(backImage)
        values.append(data['{}'.format(i)]['value'])

    frontPositions = []
    frontFeatures = []
    backPositions = []
    backFeatures = []

    for i in range(len(frontImages)):
        (keypoints, descriptors) = siftFlann.getSIFTFeatures(frontImages[i])
        frontPositions.append(keypoints)
        frontFeatures.append(descriptors)

    for i in range(len(backImages)):
        (keypoints, descriptors) = siftFlann.getSIFTFeatures(backImages[i])
        backPositions.append(keypoints)
        backFeatures.append(descriptors)

    assert(len(values) == len(frontFeatures) and len(values) == len(backFeatures)and len(values) == len(frontPositions) and len(values) == len(backPositions))

    jsonOut = []

    for i in range(len(values)):
        entry = {"value": values[i], "frontFeatures": frontFeatures[i], "backFeatures": backFeatures[i], "frontPositions": frontPositions[i], "backPositions": backPositions[i],}
        jsonOut.append(entry)
    
    with open(OUTPUT_FILE, "w") as outfile:
        outfile.write(json.dumps(jsonOut, indent=4, cls=trainingSetGeneration.NumpyArrayEncoder))
