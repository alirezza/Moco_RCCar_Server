import cv2 as cv
import numpy as np

# image size
img_width = img_height = 800

# real dimensions
width = 58.8
height = 65.5

# factor for px to distance (cm) ratio
factorX = 10 * img_width / width  # 10 * factor
factorY = 10 * img_height / height

# Load the dictionary that was used to generate the markers
dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_4X4_100)

# get LiveStream from WebCam 1
# cam = cv.VideoCapture(1)

cam = cv.VideoCapture(1, cv.CAP_DSHOW)

cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

if not cam.isOpened():
    print("Error opening video stream or file")

while cam.isOpened():

    # take current image from WebCam
    ret, frame = cam.read()

    if ret:

        # 1. detecting 4 corner tags
        # --------------------------
        output = frame.copy()

        # Initialize the detection parameters using default values
        parameters = cv.aruco.DetectorParameters_create()

        # Detect the markers in the image
        markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(frame, dictionary, parameters=parameters)

        pts1_list = [0] * 4

        if len(markerCorners):

            '''cv.aruco.drawDetectedMarkers(output, markerCorners, markerIds)
            print(markerIds)
            print(markerCorners)'''

            markerIds = markerIds.flatten()

            # zip() returns iterator of tuples,
            # each element is assigned to tuple (corner, ID)
            for (corner, ID) in zip(markerCorners, markerIds):

                # reshape to 4x2 matrix, 4 points with 2 coordinates each
                markerCorners = corner.reshape(4, 2)

                # clockwise sequence, returns pair of (x,y)-coordinates
                (topLeft, topRight, bottomRight, bottomLeft) = markerCorners

                # convert to integer
                if ID == 12:
                    pts1_list[0] = bottomRight
                    point = (int(bottomRight[0]), int(bottomRight[1]))

                if ID == 98:
                    pts1_list[1] = bottomLeft
                    point = (int(bottomLeft[0]), int(bottomLeft[1]))

                if ID == 30:
                    pts1_list[3] = topLeft
                    point = (int(topLeft[0]), int(topLeft[1]))

                if ID == 53:
                    pts1_list[2] = topRight
                    point = (int(topRight[0]), int(topRight[1]))

                try:
                    cX = point[0]
                    cY = point[1]
                    cv.circle(output, (cX, cY), 4, (0, 0, 255), -1)
                    cv.putText(output, f"x: {cX}, y: {cY}", (cX, cY - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                except NameError:
                    continue

        # Displaying the resulting frame in a window
        cv.imshow('Live Webcam', output)  # 'Live Webcam' - window name, frame - displayed image

        # 2. image transformation
        # ------------------------------
        '''print(type(pts1_list))
        print(type(pts1_list[0]))
        print(pts1_list)'''

        if all(isinstance(i, np.ndarray) for i in pts1_list):  # np.all(pts1), len(pts1) == 4

            # create new window size
            pts1 = np.asarray(pts1_list, dtype=np.float32)
            pts1_list = [0] * 4  # reset list values
            pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])

            '''cv.imwrite('test.png', output)
            print(pts1)

            break'''

            matrix = cv.getPerspectiveTransform(pts1, pts2)
            w_img = cv.warpPerspective(frame, matrix, (img_width, img_height))

            # cv.imshow('corrected image', w_img)

            # 3. detect car Aruco
            # -------------------
            '''carFrontCoordinate = carBackCoordinate = np.array([0, 0], dtype=np.float32)'''

            carMarkerCorners, carMarkerIds, rejectedCandidates = cv.aruco.detectMarkers(w_img, dictionary,
                                                                                        parameters=parameters)

            if len(carMarkerCorners):

                print("detected")
                cv.imwrite("carMarkerImages_PNG/carMarker.png", w_img)
                carMarkerIds.flatten()

                for (carCorner, carID) in zip(carMarkerCorners, carMarkerIds):

                    carMarkerCorners = carCorner.reshape(4, 2)

                    topLeft, topRight, bottomRight, bottomLeft = carMarkerCorners

                    # get coordinates
                    if carID == 1:
                        carFrontCoordinateX = int(((topLeft[0] + topRight[0]) * 0.5) * 10)
                        carFrontCoordinateY = int(((topLeft[1] + topRight[1]) * 0.5) * 10)

                    if carID == 2:
                        carBackCoordinateX = int(((bottomLeft[0] + bottomRight[0]) * 0.5) * 10)
                        carBackCoordinateY = int(((bottomLeft[1] + bottomRight[1]) * 0.5) * 10)

                try:

                    carFrontCoordinateX_display, carFrontCoordinateY_display = int(carFrontCoordinateX / 10), \
                                                                               int(carFrontCoordinateY / 10)
                    cv.circle(w_img, (carFrontCoordinateX_display, carFrontCoordinateY_display), 4, (0, 0, 255), -1)
                    cv.putText(w_img, f"x: {carFrontCoordinateX_display}, y: {carFrontCoordinateY_display}",
                               (carFrontCoordinateX_display, carFrontCoordinateY_display - 15),
                               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    print(f"distance front, x: {carFrontCoordinateX/factorX}cm")
                    print(f"distance front, y: {carFrontCoordinateY/factorY}cm")

                except NameError:
                    continue

                try:

                    carBackCoordinateX_display, carBackCoordinateY_display = int(carBackCoordinateX / 10), \
                                                                             int(carBackCoordinateY / 10)
                    cv.circle(w_img, (carBackCoordinateX_display, carBackCoordinateY_display), 4, (0, 0, 255), -1)
                    cv.putText(w_img, f"x: {carBackCoordinateX_display}, y: {carBackCoordinateY_display}",
                               (carBackCoordinateX_display, carBackCoordinateY_display - 15),
                               cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    print(f"distance back, x: {carBackCoordinateX/factorX}cm")
                    print(f"distance back, y: {carBackCoordinateY/factorY}cm")

                except NameError:
                    continue

                cv.imshow('carTags', w_img)

        # argument in waitKey in ms (between frames), ord() - returns int as Unicode
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
