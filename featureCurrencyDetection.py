import cv2 as cv
import siftFlann



DOWNSCALE_RATIO = 3
#MASTER_FOLDER = "./altValidation.json"
MASTER_FOLDER = "./validation.json"

def __checkImg(image,values, frontFeatures, backFeatures):
    
    #image = cv.imread(data['{}'.format(i)]['front'],cv.IMREAD_GRAYSCALE)
    
    image = siftFlann.downScale(image, DOWNSCALE_RATIO)

    (keypoints, descriptors) = siftFlann.getSIFTFeatures(image)

    value = siftFlann.getBillValue(descriptors, values, frontFeatures, backFeatures)
    #print(value)
    return value
    
def setup(masterFolder =MASTER_FOLDER, downscaleRatio = DOWNSCALE_RATIO):
    (values, frontFeatures, backFeatures) = siftFlann.loadValidationSet(masterFolder, downscaleRatio)
    return values, frontFeatures, backFeatures


def checkImg(values, frontFeatures, backFeatures):
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    #cv.imshow("Frame", frame)
    amount =  __checkImg(frame,values, frontFeatures, backFeatures)
    #delay needed?
    cap.release()
    #cv.destroyAllWindows() #TODO  send frame back to webapp
    return amount


  #for testing
if __name__ == '__main__':
    (values, frontFeatures, backFeatures) = siftFlann.loadValidationSet(MASTER_FOLDER, DOWNSCALE_RATIO)
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    cv.imshow("Frame", frame)

    while True:
        key = cv.waitKey(1)
        if key == 99: #c
            ret, frame = cap.read()
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            cv.imshow("Frame", frame)
        if key ==100:#d
            print(__checkImg(frame,values, frontFeatures, backFeatures))
        if key == 27:
            break

    cap.release()
    cv.destroyAllWindows()
