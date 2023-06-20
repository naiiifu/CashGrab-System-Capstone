import cv2
import matplotlib.pyplot as plt
import numpy as np


MASTER_FOLDER = "./validation.json"
THRESHOLD_VALUE = 60

sample_images = [ #5,10,20,50,100 left/right
    
    "raspicamNoPlexi/10.png",
    "raspicamNoPlexi/11.png",
    "raspicamNoPlexi/22.png",
    "raspicamNoPlexi/23.png",
    "raspicamNoPlexi/30.png",
    "raspicamNoPlexi/32.png",
    "raspicamNoPlexi/38.png",
    "raspicamNoPlexi/58.png",
    "raspicamNoPlexi/59.png",
]

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

def calculateBaseline(imgArr): #could pass key/other relevant info or handle outside
    #assume greyscale?
    img = (left,mid,right) = imgSplitVert(imgArr)
    left_count = calculate_non_zero_count(left)
    mid_count = calculate_non_zero_count(mid)
    right_count = calculate_non_zero_count(right)
    return (left_count, mid_count, right_count)

def checkCounterfeit(imgArr,baseline):#baseline is list of tuples or smth?? or better it is only for the identified bill denomination
    test = (left,mid,right)= calculateBaseline(imgArr)
    # Compare the binary masks
    pane_match = False
    for pane in test: 
        difference = cv2.subtract(pane, baseline)
        percentage_similarity = (np.count_nonzero(difference == 0) / difference.size) * 100
        if (percentage_similarity >.2):
            pane_match = True
            #could check make sure rest dont match with correct pane
            break

    return pane_match
    
    


if __name__ =="__main__":
    #real_image = "./CFphoto/23.png"
    real_image = "./CFphoto/real5.png"
    fake_image = "./CFphoto/fake11.png"
    originalR = cv2.imread(real_image)
    originalF = cv2.imread(fake_image)
    baseline = calculateBaseline(originalR)
    print("resutl {}".format(checkCounterfeit(originalF,baseline[0])))

    imgR = (left,mid,right) = imgSplitVert(originalR)
    imgF = (left,mid,right) = imgSplitVert(originalF)
    for pane in imgR:
        grey = cv2.cvtColor(pane, cv2.COLOR_BGR2GRAY)
        cv2.imshow("gg",grey)
        displayThreshold(grey)
    for pane in imgF:
        grey = cv2.cvtColor(pane, cv2.COLOR_BGR2GRAY)
        cv2.imshow("gg",grey)
        displayThreshold(grey)

