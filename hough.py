import cv2 as cv
import math

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
    binValue = HoughBin()

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
                    binValue.quantizedAngle = i
                    binValue.quantizedScale = j
                    binValue.quantizedXPoint = k
                    binValue.quantizedYPoint = l

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
    positionQuantizeStep = maxPosition * 0.25

    global matcher
    matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)

def Transform(kps1, kps2, goodMatches):
    global houghMap
    houghMap.clear()

    for match in goodMatches:
        kp1 = kps1[match.queryIdx]
        kp2 = kps2[match.trainIdx]
        _StoreDifKeypoint(kp1, kp2, match)
    
    outputMap = dict()
    output = []

    for (count, matches) in houghMap.values():
        if count >= BIN_COUNT_THRESHOLD:
            for match in matches:
                outputMap.update({match : match})
    
    # i've truely outdone myself with how bad this code is
    for match in outputMap.values():
        output.append(match)

    return output

def GetBillValue(keypoints, features, values, frontFeatures, frontFeatureVector, backFeatures, backFeatureVector):
    FEATURE_THRESHOLD = 0
    DISTANCE_RATIO = 0.7

    mostMatches = 0

    for i in range(len(frontFeatureVector)):
        matches = matcher.knnMatch(features,frontFeatureVector[i],k=2)

        goodMatches = []
        for m,n in matches:
            if m.distance < DISTANCE_RATIO*n.distance:
                goodMatches.append(m)
        
        filteredMatches = Transform(keypoints, frontFeatures[i], goodMatches)

        if len(filteredMatches) > mostMatches:
            mostMatches = len(filteredMatches)
            value = values[i]
    
    for i in range(len(backFeatureVector)):
        matches = matcher.knnMatch(features,backFeatureVector[i],k=2)

        goodMatches = []
        for m,n in matches:
            if m.distance < DISTANCE_RATIO*n.distance:
                goodMatches.append(m)
        
        filteredMatches = Transform(keypoints, backFeatures[i], goodMatches)

        if len(filteredMatches) > mostMatches:
            mostMatches = len(filteredMatches)
            value = values[i]
    
    if mostMatches >= FEATURE_THRESHOLD:
        return value
    
    return 0

