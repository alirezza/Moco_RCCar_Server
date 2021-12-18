import cv2 as cv
import numpy as np

width = height = 400

img = cv.imread('test.png')

pts1 = np.float32([[79, 73], [502, 51], [134, 443], [489, 406]])
pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

matrix = cv.getPerspectiveTransform(pts1, pts2)
w_img = cv.warpPerspective(img, matrix, (width, height))

cv.imwrite('test_w_img.png', w_img)
