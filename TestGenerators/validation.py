import json
import cv2 as cv
import os

output = "set.json"

frontPath = "./TestSet/front"
backPath = "./TestSet/back"

outputTable = [0, 5, 10, 20, 50, 100]

if __name__ == '__main__':
    # name matching
    jsonOut = {}

    i = 0

    for frontName in os.listdir(frontPath):
        front = os.path.join(frontPath, frontName)
        # checking if it is a file
        if os.path.isfile(front):
            for backName in os.listdir(backPath):
                if(frontName == backName):
                    back = os.path.join(backPath, backName)
                    # checking if it is a file
                    if os.path.isfile(back):
                        frontImage = cv.imread(front)
                        backImage = cv.imread(back)
                        cv.imshow(front,frontImage)
                        cv.imshow(back,backImage)
                        value = cv.waitKey(0)

                        # im not saying its good. im saying its functional.
                        jsonOut[i] = {
                            "front" : front,
                            "back" : back,
                            "value" : outputTable[value - 48]
                        }
                        i = i + 1

                        cv.destroyAllWindows()

    # write json
    
    with open("data.json", "w") as outfile:
        outfile.write(json.dumps(jsonOut, indent=4))