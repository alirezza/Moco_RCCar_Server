import time

import cv2 as cv
import numpy as np

# image size
img_width = img_height = 800

# real dimensions
width = 58.8
height = 65.5

# factor for px to distance (cm) ratio
factorX = 10 * img_width / width  # 10 * factor (change only this)
factorY = 10 * img_height / height

# Load the dictionary that was used to generate the markers
dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_100)
# dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)

# tagIDs
tagID_topLeft = 12
tagID_topRight = 98
tagID_bottomRight = 30
tagID_bottomLeft = 53

tagID_carFront = 1
tagID_carBack = 2

# Initialize the detection parameters using default values
parameters = cv.aruco.DetectorParameters_create()

# get LiveStream from WebCam 1
cam = cv.VideoCapture(1)

'''
# settings for camera resolution
cam = cv.VideoCapture(1, cv.CAP_DSHOW)

cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
'''

if not cam.isOpened():
    print("Error opening video stream or file")

# list for image transformation corner points
pts1_list = [0] * 4

if cam.isOpened():

    # 1. detecting 4 corner tags
    # --------------------------
    while True:

        # take current image from WebCam
        ret, initial_frame = cam.read()

        if ret:

            output = initial_frame.copy()

            # Detect the markers in the image
            markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(initial_frame, dictionary,
                                                                                  parameters=parameters)
            if len(markerCorners):

                '''
                # automated marker labeling
                cv.aruco.drawDetectedMarkers(output, markerCorners, markerIds)
                print(markerIds)
                print(markerCorners)
                '''

                markerIds = markerIds.flatten()

                # zip() returns iterator of tuples,
                # each element is assigned to tuple (corner, ID)
                for (corner, ID) in zip(markerCorners, markerIds):

                    # reshape to 4x2 matrix, 4 points with 2 coordinates each
                    markerCorners = corner.reshape(4, 2)

                    # clockwise sequence, returns pair of (x,y)-coordinates
                    (topLeft, topRight, bottomRight, bottomLeft) = markerCorners

                    # convert to integer
                    if ID == tagID_topLeft:
                        pts1_list[0] = bottomRight
                        point = (int(bottomRight[0]), int(bottomRight[1]))

                    if ID == tagID_topRight:
                        pts1_list[1] = bottomLeft
                        point = (int(bottomLeft[0]), int(bottomLeft[1]))

                    if ID == tagID_bottomRight:
                        pts1_list[3] = topLeft
                        point = (int(topLeft[0]), int(topLeft[1]))

                    if ID == tagID_bottomLeft:
                        pts1_list[2] = topRight
                        point = (int(topRight[0]), int(topRight[1]))

                    try:
                        cX = point[0]
                        cY = point[1]
                        cv.circle(output, (cX, cY), 4, (0, 0, 255), -1)
                        cv.putText(output, f"x: {cX}, y: {cY}", (cX, cY - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    except NameError:
                        continue

            cv.imshow('Corner Tags', output)  # 'Corner Tags' - window name, frame - displayed image

            # time.sleep(1)

            if all(isinstance(i, np.ndarray) for i in pts1_list):  # np.all(pts1), len(pts1) == 4

                # Displaying the resulting frame in a window
                break

    # 2. image transformation
    # -----------------------

    # create new window size
    pts1 = np.asarray(pts1_list, dtype=np.float32)
    pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])
    matrix = cv.getPerspectiveTransform(pts1, pts2)

    while True:

        ret, new_frame = cam.read()

        if ret:

            start_time_trans = time.process_time()

            warped_img = cv.warpPerspective(new_frame, matrix, (img_width, img_height))

            print(f'transformation time: {round(time.process_time() - start_time_trans, 2)}')

            # 3. detect car Aruco
            # -------------------

            start_time_detect = time.process_time()

            carMarkerCorners, carMarkerIds, rejectedCandidates = cv.aruco.detectMarkers(warped_img, dictionary,
                                                                                        parameters=parameters)

            if len(carMarkerCorners):

                carMarkerIds.flatten()

                for (carCorner, carID) in zip(carMarkerCorners, carMarkerIds):
                    print(carCorner, carID)
                    carMarkerCorners = carCorner.reshape(4, 2)

                    topLeft, topRight, bottomRight, bottomLeft = carMarkerCorners

                    # get coordinates
                    if carID == tagID_carFront:
                        carFrontCoordinateX = int(((topLeft[0] + topRight[0]) * 0.5) * 10)
                        carFrontCoordinateY = int(((topLeft[1] + topRight[1]) * 0.5) * 10)

                    if carID == tagID_carBack:
                        carBackCoordinateX = int(((bottomLeft[0] + bottomRight[0]) * 0.5) * 10)
                        carBackCoordinateY = int(((bottomLeft[1] + bottomRight[1]) * 0.5) * 10)

                try:

                    carFrontCoordinateX_display, carFrontCoordinateY_display = int(carFrontCoordinateX / 10), \
                                                                               int(carFrontCoordinateY / 10)
                    cv.circle(warped_img, (carFrontCoordinateX_display, carFrontCoordinateY_display), 4, (0, 0, 255),
                              -1)
                    cv.putText(warped_img, f"x: {carFrontCoordinateX_display}, y: {carFrontCoordinateY_display}",
                               (carFrontCoordinateX_display, carFrontCoordinateY_display - 15),
                               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    print(f"distance front, x: {carFrontCoordinateX / factorX}cm")
                    print(f"distance front, y: {carFrontCoordinateY / factorY}cm")

                except NameError:
                    continue

                try:

                    carBackCoordinateX_display, carBackCoordinateY_display = int(carBackCoordinateX / 10), \
                                                                             int(carBackCoordinateY / 10)
                    cv.circle(warped_img, (carBackCoordinateX_display, carBackCoordinateY_display), 4, (0, 0, 255),
                              -1)
                    cv.putText(warped_img, f"x: {carBackCoordinateX_display}, y: {carBackCoordinateY_display}",
                               (carBackCoordinateX_display, carBackCoordinateY_display - 15),
                               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    print(f"distance back, x: {carBackCoordinateX / factorX}cm")
                    print(f"distance back, y: {carBackCoordinateY / factorY}cm")

                except NameError:
                    continue

                cv.imshow('carTags', warped_img)

            print(f'detection time: {round(time.process_time() - start_time_detect, 2)}')

        # argument in waitKey in ms (between frames), ord() - returns int as Unicode
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
