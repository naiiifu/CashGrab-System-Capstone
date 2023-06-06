import cv2 as cv
import math
import numpy as np

BIN_COUNT_THRESHOLD = 3

ANGLE_QUANTIZE_STEP = 30
SCALE_QUANTIZE_STEP = 2

class HoughBin:
    quantizedAngle : int
    quantizedScale : int
    quantizedXPoint : int
    quantizedYPoint : int
    
    def __init__(self, quantizedAngle = 0, quantizedScale = 0, quantizedXPoint = 0, quantizedYPoint = 0):
        self.quantizedAngle = quantizedAngle
        self.quantizedScale = quantizedScale
        self.quantizedXPoint = quantizedXPoint
        self.quantizedYPoint = quantizedYPoint
    def __eq__(self, another):
        if not hasattr(another, 'quantizedAngle'):
            return False
        if not hasattr(another, 'quantizedScale'):
            return False
        if not hasattr(another, 'quantizedXPoint'):
            return False
        if not hasattr(another, 'quantizedYPoint'):
            return False
        
        if self.quantizedAngle != another.quantizedAngle:
            return False
        if self.quantizedScale != another.quantizedScale:
            return False
        if self.quantizedXPoint != another.quantizedXPoint:
            return False
        if self.quantizedYPoint != another.quantizedYPoint:
            return False
        
        return True
    def __hash__(self):
        return hash((self.quantizedAngle, self.quantizedScale, self.quantizedXPoint, self.quantizedYPoint))

def _UniformMidtreadQuantize(value, step):
    quantizedValue : int
    quantizedValue = int(math.copysign(1, value) * math.floor(abs(value - step * 0.5) / step + 0.5))

    dequantizedValue = step * float(quantizedValue)

    error = value - dequantizedValue

    if error >= step * 0.5:
        edgeAltValue = quantizedValue + 1
    else:
        edgeAltValue = quantizedValue - 1

    return [quantizedValue, edgeAltValue]

def _StoreDifKeypoint(kp1, kp2, match):
    difAngle = kp1.angle - kp2.angle
    difScale = kp1.size - kp2.size
    difXPos  = kp1.pt[0] - kp2.pt[0]
    difYPos  = kp1.pt[1] - kp2.pt[1]

    angleBins = _UniformMidtreadQuantize(difAngle, ANGLE_QUANTIZE_STEP)
    scaleBins = _UniformMidtreadQuantize(difScale, SCALE_QUANTIZE_STEP)

    global positionQuantizeStep
    xBins = _UniformMidtreadQuantize(difXPos, positionQuantizeStep)
    yBins = _UniformMidtreadQuantize(difYPos, positionQuantizeStep)
    
    global houghMap
    for i in angleBins:
        for j in scaleBins:
            for k in xBins:
                for l in yBins:
                    binValue = HoughBin(i, j, k, l)

                    (count, matches) = houghMap.get(binValue, (0, list()))
                    if(count == 0):
                        # i hate python
                        matches = [match]
                    else:
                        matches.append(match)
                    count = count + 1

                    houghMap.update({binValue: (count, matches)}) 

def SetUp(trainingImageDescriptors):
    global houghMap
    houghMap = {}

    maxPosition = 0.0
    
    for imageDescriptorSet in trainingImageDescriptors:
        for descriptor in imageDescriptorSet:
            if descriptor.pt[0] > maxPosition:
                maxPosition = descriptor.pt[0]
            if descriptor.pt[1] > maxPosition:
                maxPosition = descriptor.pt[1]
    
    global positionQuantizeStep
    # positionQuantizeStep = maxPosition * 0.25
    positionQuantizeStep = 160

    global matcher
    matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)

def HoughTransform(kps1, kps2, goodMatches):
    global houghMap
    houghMap.clear()

    for match in goodMatches:
        kp1 = kps1[match.queryIdx]
        kp2 = kps2[match.trainIdx]
        _StoreDifKeypoint(kp1, kp2, match)

    return houghMap
    
    # outputMap = dict()
    # output = []

    # for (count, matches) in houghMap.values():
    #     if count >= BIN_COUNT_THRESHOLD:
    #         for match in matches:
    #             outputMap.update({match : match})
    
    # i've truely outdone myself with how bad this code is
    # for match in outputMap.values():
    #     output.append(match)

    # return output

def GetGoodMatches(inputFeatures, testFeatures):
    DISTANCE_RATIO = 0.7
    matches = matcher.knnMatch(inputFeatures,testFeatures,k=2)

    goodMatches = []
    for m,n in matches:
        if m.distance < DISTANCE_RATIO*n.distance:
            goodMatches.append(m)
    
    return (matches, goodMatches)

def GetMatchingPoints(matches, inputKeypoints, testKeypoints):
    inputPositions = []
    testPositions = []

    for match in matches:
        inputKeypoint = inputKeypoints[match.queryIdx]
        inputPositions.append(inputKeypoint.pt)

        testKeypoint = testKeypoints[match.trainIdx]
        testPositions.append(testKeypoint.pt)

    inputPositions = np.array(inputPositions, dtype=np.float32)
    testPositions = np.array(testPositions, dtype=np.float32)
    return (inputPositions, testPositions)

def GetAffineInliers(inputKeypoints, featureMatches,  testKeypoints, transform):
    global positionQuantizeStep

    if(transform[0] is None):
        return 0

    errorThreshold = 40 * 40

    transform = np.array(transform[0], dtype=np.float32)

    m = transform[0:2, 0:2]
    t = transform[0:2, 2]

    inliers = 0
    
    for (match, _other) in featureMatches:
        inputPoint =  inputKeypoints[match.queryIdx]
        inputPoint = np.array(inputPoint.pt, dtype=np.float32)

        testPoint = testKeypoints[match.trainIdx]
        testPoint = np.array(testPoint.pt, dtype=np.float32)

        
        transformedInput = np.matmul(inputPoint, m)
        transformedInput = transformedInput + t

        deltaPosition = testPoint - transformedInput

        if np.dot(deltaPosition, deltaPosition) < errorThreshold:
            inliers = inliers + 1

    return inliers


def GetBillValue(keypoints, features, values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector, featureCount = False):
    FEATURE_THRESHOLD = 0

    mostMatches = 0
    nextMostMatches = 0
    dbFeatures = 0

    for i in range(len(frontFeatureVector)):
        (featureMatches, goodMatches) = GetGoodMatches(features, frontFeatureVector[i])
        
        houghTransform = HoughTransform(keypoints, frontFeatures[i], goodMatches)

        for (count, matches) in houghTransform.values():
            if count >= BIN_COUNT_THRESHOLD:
                (inputPoints, testPoints) = GetMatchingPoints(matches, keypoints, frontFeatures[i])
                affineTransform = cv.estimateAffine2D(inputPoints, testPoints)
                inliers = GetAffineInliers(keypoints, featureMatches, frontFeatures[i], affineTransform)

                if inliers > mostMatches:
                    mostMatches = inliers
                    value = values[i]

        # if len(filteredMatches) <= mostMatches and len(filteredMatches) > nextMostMatches:
        #     nextMostMatches = len(filteredMatches)

        # if len(filteredMatches) > mostMatches:
        #     mostMatches = len(filteredMatches)
        #     value = values[i]
        #     dbFeatures = len(frontFeatureVector[i])
    
    for i in range(len(backFeatureVector)):
        (featureMatches, goodMatches) = GetGoodMatches(features, backFeatureVector[i])
        
        houghTransform = HoughTransform(keypoints, backFeatures[i], goodMatches)

        for (count, matches) in houghTransform.values():
            if count >= BIN_COUNT_THRESHOLD:
                (inputPoints, testPoints) = GetMatchingPoints(matches, keypoints, backFeatures[i])
                affineTransform = cv.estimateAffine2D(inputPoints, testPoints)
                inliers = GetAffineInliers(keypoints, featureMatches, backFeatures[i], affineTransform)

                if inliers > mostMatches:
                    mostMatches = inliers
                    value = values[i]
    
    if mostMatches >= FEATURE_THRESHOLD:
        if featureCount:
            return (value, mostMatches, nextMostMatches, dbFeatures)
        return value
    if featureCount:
        return (0, mostMatches, nextMostMatches, dbFeatures)
    return value

