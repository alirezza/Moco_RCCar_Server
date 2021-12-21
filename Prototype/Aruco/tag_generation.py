import cv2 as cv
import numpy as np

# load dictionary of tag images 6x6 bit binary pattern
tagDict = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_100)
# tagDict = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)

''''''
# generate tag images for each corner
tagImage_topLeft = np.zeros((900, 900), dtype=np.uint8)
tagImage_topRight = np.zeros((900, 900), dtype=np.uint8)
tagImage_bottomLeft = np.zeros((900, 900), dtype=np.uint8)
tagImage_bottomRight = np.zeros((900, 900), dtype=np.uint8)

tagImage_topLeft = cv.aruco.drawMarker(tagDict, 12, 900, tagImage_topLeft, 1)
tagImage_topRight = cv.aruco.drawMarker(tagDict, 98, 900, tagImage_topRight, 1)
tagImage_bottomRight = cv.aruco.drawMarker(tagDict, 30, 900, tagImage_bottomRight, 1)
tagImage_bottomLeft = cv.aruco.drawMarker(tagDict, 53, 900, tagImage_bottomLeft, 1)


# store tags in tagImages_PNG folder
cv.imwrite("tagImages_PNG/tag_topLeft.png", tagImage_topLeft)
cv.imwrite("tagImages_PNG/tag_topRight.png", tagImage_topRight)
cv.imwrite("tagImages_PNG/tag_bottomLeft.png", tagImage_bottomLeft)
cv.imwrite("tagImages_PNG/tag_bottomRight.png", tagImage_bottomRight)
''''''

tagImage_carFront = np.zeros((400, 400), dtype=np.uint8)
tagImage_carBack = np.zeros((400, 400), dtype=np.uint8)

tagImage_carFront = cv.aruco.drawMarker(tagDict, 21, 400, tagImage_carFront, 1)
tagImage_carBack = cv.aruco.drawMarker(tagDict, 89, 400, tagImage_carBack, 1)

cv.imwrite("tagImages_PNG/tag_carFront.png", tagImage_carFront)
cv.imwrite("tagImages_PNG/tag_carBack.png", tagImage_carBack)
