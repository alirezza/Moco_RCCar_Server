import cv2 as cv
import numpy as np

factorX = 10 * 6.802721088435374  # 10 * factor
factorY = factorX

w_img = cv.imread('carMarkerImages_PNG/carMarker.png')

# Load the dictionary that was used to generate the markers.
dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_6X6_250)

parameters = cv.aruco.DetectorParameters_create()
carMarkerCorners, carMarkerIds, rejectedCandidates = cv.aruco.detectMarkers(w_img, dictionary,
                                                                            parameters=parameters)
while True:
    if len(carMarkerCorners):

        print("detected")
        cv.imwrite("carMarkerImages_PNG/carMarker.png", w_img)
        carMarkerIds.flatten()

        for (carCorner, carID) in zip(carMarkerCorners, carMarkerIds):

            print(carCorner)  # Warum 2. car corner nur 1 koordinate? bzw. warum wird koordinate angezeigt, wenn carback nicht detected werden kann
            if carCorner.size() == 4:
                carMarkerCorners = carCorner.reshape(4, 2)

            topLeft, topRight, bottomRight, bottomLeft = carMarkerCorners

            # get coordinates
            if carID == 21:
                # print(type(bottomRight[0]))
                carFrontCoordinateX = int(((topLeft[0] + topRight[0]) * 0.5) * 10)
                # print(carFrontCoordinateX)
                # print(type(carFrontCoordinateX))
                carFrontCoordinateY = int(((topLeft[1] + topRight[1]) * 0.5) * 10)

                # carFrontCoordinate = (carFrontCoordinateX, carFrontCoordinateY)

            if carID == 89:
                carBackCoordinateX = (int(bottomLeft[0]) + int(bottomRight[0])) * 0.5
                carBackCoordinateY = (int(bottomLeft[1]) + int(bottomRight[1])) * 0.5

                # carBackCoordinate = (carBackCoordinateX, carBackCoordinateY)

        if carFrontCoordinateX and carFrontCoordinateY:
            carFrontCoordinateX_display = int(carFrontCoordinateX / 10)
            carFrontCoordinateY_display = int(carFrontCoordinateY / 10)
            cv.circle(w_img, (carFrontCoordinateX_display, carFrontCoordinateY_display), 4, (0, 0, 255), -1)
            cv.putText(w_img, f"x: {carFrontCoordinateX_display}, y: {carFrontCoordinateY_display}",
                       (carFrontCoordinateX_display, carFrontCoordinateY_display - 15),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            print(f"distance front, x: {carFrontCoordinateX / factorX}cm")
            print(f"distance front, y: {carFrontCoordinateY / factorY}cm")
            cv.imshow('carTags', w_img)

        try:
            if carBackCoordinateX and carBackCoordinateY:
                cv.circle(w_img, (carBackCoordinateX, carBackCoordinateY), 4, (0, 0, 255), -1)
                cv.putText(w_img, f"x: {carBackCoordinateX}, y: {carBackCoordinateY}",
                           (carBackCoordinateX, carBackCoordinateY - 15),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                print(f"distance back, x: {carBackCoordinateX / factorX}")
                print(f"distance back, y: {carBackCoordinateY / factorY}")

        except NameError:
            continue

        cv.imshow('carTags', w_img)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break
