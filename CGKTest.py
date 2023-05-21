import cv2 as cv
import numpy as np

import orbFeatures
import kmeans
import LPP

if __name__ == "__main__":
    im = cv.imread("./val/PXL_20230302_062303342.jpg")

    descriptors = orbFeatures.getORBDescriptors(im)

    npDescriptors = np.float32(descriptors)

    (labels, centers) = kmeans.getKMeans(npDescriptors)

    (dim4, dim8) = LPP.getLLP(centers)

    print(":)")