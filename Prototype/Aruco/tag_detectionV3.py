import math
import time

import cv2 as cv
import numpy as np


def displayimage(window_name, input_image):
    while True:
        cv.imshow(window_name, input_image)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


# image size for warped image
img_width = img_height = 720

# real dimensions (cm)
width = 71  # 58.8
height = 44  # 65.5

# factor for px to distance (cm) ratio
factorX = img_width / width
factorY = img_height / height

# Load the dictionary that was used to generate the markers
dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_100)

# tagIDs
tagID_topLeft = 12
tagID_topRight = 98
tagID_bottomRight = 30
tagID_bottomLeft = 53

# Initialize the detection parameters using default values
parameters = cv.aruco.DetectorParameters_create()

# get LiveStream from WebCam
# cam = cv.VideoCapture(0)

# settings for camera resolution
cam = cv.VideoCapture(1, cv.CAP_DSHOW)

cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

if not cam.isOpened():
    print("Error opening video stream or file")

if cam.isOpened():

    # list for image transformation corner points
    pts1_list = [0] * 4

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

                for point in pts1_list:
                    print('myType: ', type(point))
                    if type(point) == np.ndarray:
                        x = int(point[0])
                        y = int(point[1])
                        cv.circle(output, (x, y), 4, (0, 0, 255), -1)
                        cv.putText(output, f"x: {x}, y: {y}", (x, y - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # Displaying the resulting frame in a window
            cv.imshow('Corner Tags', output)

            if all(isinstance(i, np.ndarray) for i in pts1_list) or cv.waitKey(1) & 0xFF == ord('q'):
                displayimage('Corner Tags', output)
                break

    # 2. image transformation
    # -----------------------

    # create new window size
    pts1 = np.asarray(pts1_list, dtype=np.float32)
    pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])
    matrix = cv.getPerspectiveTransform(pts1, pts2)

    while True:

        ret, new_frame = cam.read()

        start_time = time.process_time()

        if ret:
            warped_img = cv.warpPerspective(new_frame, matrix, (img_width, img_height))
            cv.imwrite('track.png', warped_img)
            # print(f'transformation time: {round(time.process_time() - start_time_trans, 2)}')

            # 3. detect car Aruco
            # -------------------

            # start_time_detect = time.process_time()

            carMarkerCorners, carMarkerIds, rejectedCandidates = cv.aruco.detectMarkers(warped_img, dictionary,
                                                                                        parameters=parameters)

            try:
                if len(carMarkerIds.tolist()) == 1:
                    for (carCorner, carID) in zip(carMarkerCorners, carMarkerIds):

                        carMarkerCorners = carCorner.reshape(4, 2)

                        # get coordinates
                        topLeft, topRight, bottomRight, bottomLeft = carMarkerCorners

                        carCoordinateX = int((topLeft[0] + bottomRight[0]) / 2.0)
                        carCoordinateY = int((topLeft[1] + bottomRight[1]) / 2.0)
                        cv.circle(warped_img, (carCoordinateX, carCoordinateY), 4, (0, 0, 255), -1)
                        cv.putText(warped_img, f"x: {carCoordinateX}, y: {carCoordinateY}",
                                   (carCoordinateX, carCoordinateY - 15),
                                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                        print(f"distance, x: {round(carCoordinateX / factorX, 2)}cm")
                        print(f"distance, y: {round(carCoordinateY / factorY, 2)}cm")

                        if not (topLeft[0] == bottomLeft[0] and topLeft[1] == bottomLeft[1]):

                            headingAngle = np.arctan2(bottomLeft[0] - topLeft[0], topLeft[1] - bottomLeft[1])

                            if headingAngle < 0:
                                headingAngle = headingAngle + 2 * math.pi

                            print(f"heading angle: {round(np.rad2deg(headingAngle), 2)}")

                    cv.imshow('carTags', warped_img)

                # print(f'{int(1 / (round(time.process_time() - start_time, 2)))}fps')  # fps = 1s / time per frame

            except AttributeError:
                continue

            # argument in waitKey in ms (between frames), ord() - returns int as Unicode
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

# When everything done, release the capture
cam.release()  # close IO device, i.e. camera
cv.destroyAllWindows()  # close windows (out of loop)
