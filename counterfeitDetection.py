import cv2 
import numpy as np

import currencyDetection

MASTER_FOLDER = "./validation.json"
validationPath = "./piValidation.json"

THRESHOLD_VALUE = 60
PERCENT_TOLERANCE = 0.7

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
    difference = cv2.subtract(input, reference)
    percentage_similarity = (np.count_nonzero(difference == 0) / difference.size) * 100
    if (percentage_similarity > PERCENT_TOLERANCE):
        return True
    else:
        print("Rejected with similairty {percentage_similarity}")
    return False

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

def detectCF(imgArr):
    cv2.imshow(":(",imgArr)
    cv2.waitKey(0)
    #currencyDetection.SetUp(validationPath)

    #inputImage = cv2.imread(inputImagePath)
    inputImage = imgArr
    (value, error) = currencyDetection.Detect(inputImage)

    if value == 0:
        print("Bill not detected!")
        return False
    
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
    return checkCounterfeit_percent(countInput,countBaseline)

    cv2.imshow("reference", referenceWindow)
    cv2.imshow("input", inputWindow)
    calculateBaseline(referenceWindow)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #return checkCounterfeit_percent(countInput,countBaseline)



def Demo():
    inputImagePath = "./val/trainingData/raspicamNoPlexi/13.png"
    validationPath = "./piValidation.json"

    currencyDetection.SetUp(validationPath)

    inputImage = cv2.imread(inputImagePath)
    (value, error) = currencyDetection.Detect(inputImage)

    if value == 0:
        print("Bill not detected!")
        return
    
    affineTransform = currencyDetection.getAffineTransform()
    referenceIndex = currencyDetection.getMatchIndex()

    # needs to be downscaled since we only store the downscaled version of the reference image
    downscaledImage = currencyDetection.DownScale(inputImage, currencyDetection.DOWNSCALE_RATIO)

    referenceWindow = getReferenceTransparentWindow(referenceIndex)
    inputWindow = getInputTransparentWindow(downscaledImage, referenceIndex, affineTransform)

    cv2.imshow("reference", referenceWindow)
    cv2.imshow("input", inputWindow)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ =="__main__":
    #Demo()
    currencyDetection.SetUp(validationPath)
    #real_image = "./val/CFphoto/23.png"
    real_image = "./val/trainingData/raspicamNoPlexi/13.png"
    fake_image = "./val/CFphoto/fake11.png"

    originalR = cv2.imread(real_image)
    originalF = cv2.imread(fake_image)
    assert detectCF(originalR)
    assert not detectCF(originalF)
 

