import cv2 
import numpy as np
import json
import currencyDetection

#copied form currencyDetection.py may need to remove later
import csv
import cProfile
import pstats, io
from pstats import SortKey
pr = cProfile.Profile()

#######

MASTER_FOLDER = "./finalVal.json"
validationPath = "./piValidation.json"

DEBUG_MODE = True


THRESHOLD_VALUE = 60
#PERCENT_TOLERANCE = 0.7
PERCENT_RANGE = 0.64350938169

def imgSplitHrz(img):
    h, w, channels = img.shape
    
    # this is horizontal division
    half2 = h//2
    
    top = img[:half2, :]
    bottom = img[half2:, :]
    
    return top,bottom

def imgSplitVert(img):
    h, w, channels = img.shape
    
    third = w//3    
    # this will be the first column
    left = img[:, :third]
    mid = img[:,third:2*third]
    right = img[:,2*third:]
    
    return left,mid,right


def displayThreshold(img):
    ret,binary_mask = cv2.threshold(img,THRESHOLD_VALUE,255,cv2.THRESH_BINARY_INV)
    print("non zero {}".format(cv2.countNonZero(binary_mask)))
    cv2.imshow(":(",binary_mask)
    bruh = cv2.waitKey(0)



def calculate_non_zero_count(imgArr, threshold_value=THRESHOLD_VALUE):

    #could threshold unneeded blacks? or cut/crop source image to avoid stand
    ret, binary_mask = cv2.threshold(imgArr, threshold_value, 255, cv2.THRESH_BINARY_INV)
    count = np.count_nonzero(binary_mask)

    return count

def calculatePaneBaselines(imgArr): #could pass key/other relevant info or handle outside
    #assume greyscale?
    img = (left,mid,right) = imgSplitVert(imgArr)
    left_count = calculate_non_zero_count(left)
    mid_count = calculate_non_zero_count(mid)
    right_count = calculate_non_zero_count(right)
    return (left_count, mid_count, right_count)

def DEPRECATEDcheckCounterfeit_percent(imgArr,baseline):#baseline is list of tuples or smth?? or better it is only for the identified bill denomination
    test = (left,mid,right)= calculatePaneBaselines(imgArr)
    # Compare the binary masks
    pane_match = False
    for pane in test: 
        difference = cv2.subtract(pane, baseline)
        percentage_similarity = (np.count_nonzero(difference == 0) / difference.size) * 100
        if (percentage_similarity >.2):
            pane_match = True
            #could check make sure rest dont match with correct pane\
            
            break

    return pane_match


def checkCounterfeit_percent(input,reference):#baseline is list of tuples or smth?? or better it is only for the identified bill denomination
    upperlimit = reference*(1+PERCENT_RANGE)
    lowerlimit = reference*(1-PERCENT_RANGE)
    percentdiff = 100*abs(input-reference)/((input+reference)/2)
    if(input <= upperlimit and input >= lowerlimit):
        return False, percentdiff
    else:
        #if DEBUG_MODE:
        #print("Rejected with similairty {}".format(percentdiff))
        print(f"counted: {input} outside threshold lower: {lowerlimit}, uppe: {upperlimit}")
        print(f"percet value {abs(input / reference - 1)}")
    return True , percentdiff

# def checkCounterfeit_percent(input,reference):#baseline is list of tuples or smth?? or better it is only for the identified bill denomination
#     difference = cv2.subtract(input, reference)
#     percentage_similarity = (np.count_nonzero(difference == 0) / difference.size) * 100
#     if (percentage_similarity > PERCENT_TOLERANCE):
#         return True , percentage_similarity
#     else:
#         if DEBUG_MODE:
#             print("Rejected with similairty {percentage_similarity}")
#     return False , percentage_similarity

# expects to be given the points on the reference bill, and the affine transform returned by RANSAC
# affine transform is from input image space to reference image space
def inverseTransformPoints(referencePoints, affineTransform):
    transformInput = np.float32(referencePoints).reshape(-1,1,2)

    inverseAffineTransform = np.linalg.inv(affineTransform)

    transformOutput = cv2.perspectiveTransform(transformInput, inverseAffineTransform)

    return transformOutput

def getPointBoundSubimage(points, image):
    minX = float("inf")
    maxX = -float("inf")
    minY = float("inf")
    maxY = -float("inf")

    for i in range(0, len(points)):
        point = points[i]
        minX = min(minX, point[0])
        maxX = max(maxX, point[0])
        minY = min(minY, point[1])
        maxY = max(maxY, point[1])

    minX = int(minX)
    maxX = int(maxX)
    minY = int(minY)
    maxY = int(maxY)

    croppedImage = image[minY:maxY, minX:maxX]

    return croppedImage

def getReferenceTransparentWindow(referenceIndex):
    referenceImage = currencyDetection.getReferenceImage(referenceIndex)
    referencePoints = currencyDetection.getReferencePoints(referenceIndex)

    croppedReferenceImage = getPointBoundSubimage(referencePoints, referenceImage)

    return croppedReferenceImage

def getInputTransparentWindow(inputImage, referenceIndex, affineTransform):
    points = currencyDetection.getReferencePoints(referenceIndex)

    transformedPoints = inverseTransformPoints(points, affineTransform)

    transformedPoints = transformedPoints.tolist()

    for i in range(0, len(transformedPoints)):
        point = transformedPoints[i]
        point = point[0]
        transformedPoints[i] = point

    return getPointBoundSubimage(transformedPoints, inputImage)

def uncalculated_detectCF(imgArr):
    if DEBUG_MODE:
        cv2.namedWindow("input", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("input", 800, 600)
        cv2.imshow("input",imgArr)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    #currencyDetection.SetUp(validationPath) enable if this isnt run being after currency detection fro some reason

    #inputImage = cv2.imread(inputImagePath)
    inputImage = imgArr
    (value, error) = currencyDetection.Detect(inputImage)

    if value == 0:
        #if DEBUG_MODE:
        print("Bill not detected!")
        return True, -1
    
    affineTransform = currencyDetection.getAffineTransform()
    referenceIndex = currencyDetection.getMatchIndex()

    # needs to be downscaled since we only store the downscaled version of the reference image
    downscaledImage = currencyDetection.DownScale(inputImage, currencyDetection.DOWNSCALE_RATIO)

    referenceWindow = getReferenceTransparentWindow(referenceIndex)
    inputWindow = getInputTransparentWindow(downscaledImage, referenceIndex, affineTransform)
    inputWindowGRAY = cv2.cvtColor(inputWindow, cv2.COLOR_BGR2GRAY)
    referenceWindowGRAY = cv2.cvtColor(referenceWindow, cv2.COLOR_BGR2GRAY)
    countBaseline = calculate_non_zero_count(referenceWindowGRAY)
    countInput = calculate_non_zero_count(inputWindowGRAY)
    
    #return checkCounterfeit_percent(countInput,countBaseline)
    if DEBUG_MODE:
        cv2.imshow("reference", referenceWindow)
        cv2.imshow("input", inputWindow)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    (result, percent) = checkCounterfeit_percent(countInput,countBaseline)
    return result, percent



def detectCF(inputImage,value):
    if value < 5:
        #if DEBUG_MODE:
        print("Bill not detected!")
        return True, -1
    if DEBUG_MODE:
        {}
        # print("debug output image")
        # cv2.namedWindow("input", cv2.WINDOW_NORMAL)
        # cv2.resizeWindow("input", 800, 600)
        # cv2.imshow("input",inputImage)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # print("debug end output image")
    
    #currencyDetection.SetUp(validationPath) enable if this isnt run being after currency detection fro some reason
    #inputImage = cv2.imread(inputImagePath)
   
    
    affineTransform = currencyDetection.getAffineTransform()
    referenceIndex = currencyDetection.getMatchIndex()

    # needs to be downscaled since we only store the downscaled version of the reference image
    downscaledImage = currencyDetection.DownScale(inputImage, currencyDetection.DOWNSCALE_RATIO)

    referenceWindow = getReferenceTransparentWindow(referenceIndex)
    inputWindow = getInputTransparentWindow(downscaledImage, referenceIndex, affineTransform)
    inputWindowGRAY = cv2.cvtColor(inputWindow, cv2.COLOR_BGR2GRAY)
    referenceWindowGRAY = cv2.cvtColor(referenceWindow, cv2.COLOR_BGR2GRAY)
    countBaseline = calculate_non_zero_count(referenceWindowGRAY)
    countInput = calculate_non_zero_count(inputWindowGRAY)
    
    #return checkCounterfeit_percent(countInput,countBaseline)
    if DEBUG_MODE:
        {}
        #cv2.imshow("reference", referenceWindow)
        #cv2.imshow("input", inputWindow)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
    (result, percent) = checkCounterfeit_percent(countInput,countBaseline)
    return result, percent

if __name__ =="__main__":
    keyPath = "./piValidation.json"
    currencyDetection.SetUp(keyPath)


    # trainingPath = "./raspiCamTrainingSet.json"
    trainingPath = "./finalValCombined.json"

    pr.enable()

    currencyDetection.SetUp(keyPath)

    with open("full_CF2.csv", 'w') as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["RealValue", "TestValue", "Error","Fake","Percent","Guess"])

        trainingFile = open(trainingPath)
        trainingJson = json.load(trainingFile)

        for entry in trainingJson:
            image = cv2.imread(entry['path'])
            inputValue = entry['value']

            (value, error) = currencyDetection.Detect(image)
            (result, percent) = uncalculated_detectCF(image)

            writer.writerow([inputValue, value, error,entry['fake'],percent,result])
    
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

