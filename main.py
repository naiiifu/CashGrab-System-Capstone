import cv2 as cv
import numpy as np
import hough

if __name__ == "__main__":
    im1 = cv.imread("val/trainingData/noPlexi/16.png")
    im2 = cv.imread("val/PXL_20230302_045356412.jpg")

    im1 = cv.resize(im1, [756, 567], interpolation=cv.INTER_AREA)
    im2 = cv.resize(im2, [567, 756], interpolation=cv.INTER_AREA)

    sift = cv.SIFT_create()
    kp1 = sift.detect(im1)
    kp2 = sift.detect(im2)

    (loc1, dec1) = sift.compute(im1, kp1)
    (loc2, dec2) = sift.compute(im2, kp2)

    matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
    knn_matches = matcher.knnMatch(dec1, dec2, 2)
    #-- Filter matches using the Lowe's ratio test
    ratio_thresh = 0.8
    good_matches = []
    for m,n in knn_matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)

    hough.SetUp([loc1])

    res = hough.Transform(loc1, loc2, good_matches)

    out = np.empty((max(im1.shape[0], im2.shape[0]), im1.shape[1]+im2.shape[1], 3), dtype=np.uint8)
    cv.drawMatches(im1, loc1, im2, loc2, res, out, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv.imshow(":)",out)
    cv.drawMatches(im1, loc1, im2, loc2, good_matches, out, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv.imshow(":()",out)
    cv.waitKey(0)
    {}