from StateLib import *
import cv2 as cv
import numpy as np
import time, math
from State_PathDetect import StatePathDetect
from Configuration import ServerConfig


class StateCornerDetection(State):
    tagID_topLeft = 0
    tagID_topRight = 0
    tagID_bottomRight = 0
    tagID_bottomLeft = 0
    dictionary = 0
    parameters = 0
    cam = 0
    pts1_list = 0
    detectionComplete = False

    def run(self):

        if self.cam.isOpened():
            ret, initial_frame = self.cam.read()
            # cv.imshow('Corner Tags', initial_frame)

            if ret:
                output = initial_frame.copy()

                # Detect the markers in the image
                markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(initial_frame, self.dictionary,
                                                                                      parameters=self.parameters)
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
                        if ID == self.tagID_topLeft:
                            self.pts1_list[0] = bottomRight
                            point = (int(bottomRight[0]), int(bottomRight[1]))

                        if ID == self.tagID_topRight:
                            self.pts1_list[1] = bottomLeft
                            point = (int(bottomLeft[0]), int(bottomLeft[1]))

                        if ID == self.tagID_bottomRight:
                            self.pts1_list[3] = topLeft
                            point = (int(topLeft[0]), int(topLeft[1]))

                        if ID == self.tagID_bottomLeft:
                            self.pts1_list[2] = topRight
                            point = (int(topRight[0]), int(topRight[1]))

                    for point in self.pts1_list:
                        if type(point) == np.ndarray:
                            x = int(point[0])
                            y = int(point[1])
                            cv.circle(output, (x, y), 4, (0, 0, 255), -1)
                            cv.putText(output, f"x: {x}, y: {y}", (x, y - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                                       1)

                cv.imshow('Corner Tags', output)
                cv.waitKey(1)

                if all(isinstance(i, np.ndarray) for i in self.pts1_list):
                    # displayimage('Corner Tags', output)
                    self.detectionComplete = True

    def next(self):
        if self.detectionComplete:
            time.sleep(1)
            cv.destroyWindow('Corner Tags')
            return StatePathDetect(self.pts1_list)
        else:
            return self

    def on_enter(self):

        self.tagID_topLeft = 65
        self.tagID_topRight = 85
        self.tagID_bottomRight = 0
        self.tagID_bottomLeft = 63

        self.dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_ARUCO_ORIGINAL)
        self.parameters = cv.aruco.DetectorParameters_create()
        self.cam = cv.VideoCapture(ServerConfig.getInstance().CamSelect)

        '''self.cam.set(cv.CAP_PROP_FRAME_WIDTH, ServerConfig.getInstance().FrameWidth)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, ServerConfig.getInstance().FrameHeight)'''
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, ServerConfig.getInstance().FrameWidth)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, ServerConfig.getInstance().FrameHeight)

        self.pts1_list = [0] * 4
        self.detectionComplete = False

        if not self.cam.isOpened():
            print("Error opening video stream or file")  # Assertion?

        print("Enter Complete")

    def on_leave(self):

        self.cam.release()
        print("Corner Detection Complete")
