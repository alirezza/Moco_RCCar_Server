from StateLib import *
from State_ControlCar import *
import cv2 as cv
import numpy as np
from Configuration import ServerConfig
import pickle
import time


class StatePathDetect(State):
    pts1_list = 0
    path_list = 0
    path_list_cm = 0
    cam = 0
    img_width = ServerConfig.getInstance().FrameWidth
    img_height = ServerConfig.getInstance().FrameHeight
    matrix = 0

    # factor for px to distance (cm) ratio
    factorX = 0
    factorY = 0

    # real dimensions (cm)
    width = ServerConfig.getInstance().TrackWidth
    height = ServerConfig.getInstance().TrackHeight

    usepath = False

    def __init__(self, pts):
        self.pts1_list = pts

    def next(self):

        if self.usepath:
            return StateControlCar(self.pts1_list, self.path_list)

        # if(type == 1) return StateControlCar(pts, prerecordedpath)
        # if(type == 2) return StateControlCar(pts, edgedetectionpath)

        else:
            return self

    def run(self):

        ret, new_frame = self.cam.read()

        if ret:
            warped_img = cv.warpPerspective(new_frame, self.matrix, (self.img_width, self.img_height))
            self.draw_tag_border(warped_img)
            self.draw_grid(warped_img)
            for point in self.path_list:
                cv.circle(warped_img, (point[0], point[1]), 4, (0, 255, 255), -1)

            if len(self.path_list) >= 1 + ServerConfig.getInstance().lookback_n + ServerConfig.getInstance().lookahead_n:
                cv.polylines(warped_img, [np.array(self.path_list)], True, (0, 255, 0), 3)

            cv.imshow('Warped Img', warped_img)
            k = cv.waitKey(20) & 0xFF

    def on_enter(self):

        print("Enter Path Detect State")

        pts1 = np.asarray(self.pts1_list, dtype=np.float32)
        pts2 = np.float32([[0, 0],
                           [self.img_width, 0],
                           [0, self.img_height],
                           [self.img_width, self.img_height]])
        self.matrix = cv.getPerspectiveTransform(pts1, pts2)
        self.cam = cv.VideoCapture(ServerConfig.getInstance().CamSelect)
        self.path_list = []
        self.path_list_cm = []

        # factor for px to distance (cm) ratio
        self.factorX = self.img_width / self.width
        self.factorY = self.img_height / self.height

        cv.namedWindow('Warped Img')
        cv.setMouseCallback('Warped Img', self.get_mouse_pos)

        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, ServerConfig.getInstance().FrameWidth)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, ServerConfig.getInstance().FrameHeight)

        if not self.cam.isOpened():
            print("Error opening video stream or file")

        print("Enter Path Detect State")

    def on_leave(self):
        print("Path Detect Complete")
        self.cam.release()
        cv.destroyWindow('Warped Img')

    def get_mouse_pos(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.path_list.append([x, y])
            # print(self.path_list)
            self.path_list_cm.append([x / self.factorX, y / self.factorY])
            print(self.path_list_cm)

    def set_use_path(self, flag):
        if len(self.path_list) < 3:
            self.usepath = False
        else:
            self.usepath = flag

        if not flag:
            self.path_list = []

    def save_trajectory(self, path):
        with open(path, 'wb') as handle:
            pickle.dump(self.path_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print("Path Saved")
            # print(self.path_list)

    def load_trajectory(self, path):
        with open(path, 'rb') as handle:
            self.path_list = pickle.load(handle)
            print("Path Loaded")
            # print(self.path_list)

    def draw_grid(self,img, line_color=(0, 255, 0), thickness=1, type_=cv.LINE_AA, x_pxstep=int(15*(img_width/width)), y_pxstep=int(15*(img_height/height))):
        '''(ndarray, 3-tuple, int, int) -> void
        draw gridlines on img
        line_color:
            BGR representation of colour
        thickness:
            line thickness
        type:
            8, 4 or cv2.LINE_AA
        x_pxstep:
            grid line frequency in pixels
        y_pxstep:
            grid line frequency in pixels
        '''
        x = x_pxstep
        y = y_pxstep

        while x < img.shape[1]:
            cv.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
            x += x_pxstep

        while y < img.shape[0]:
            cv.line(img, (0, y), (img.shape[1], y), color=line_color, lineType=type_, thickness=thickness)
            y += y_pxstep

    def draw_tag_border(self,img):
        arucoDict = cv.aruco.Dictionary_get(cv.aruco.DICT_ARUCO_ORIGINAL)
        arucoParams = cv.aruco.DetectorParameters_create()
        corners, ids, rejectedCandidates = cv.aruco.detectMarkers(img, arucoDict,
                                                                                    parameters=arucoParams)
        if len(corners) > 0:
            # flatten the ArUco IDs list
            ids = ids.flatten()
            # loop over the detected ArUCo corners
            for (markerCorner, markerID) in zip(corners, ids):
                # extract the marker corners (which are always returned in
                # top-left, top-right, bottom-right, and bottom-left order)
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))
                # draw the bounding box of the ArUCo detection
                cv.line(img, topLeft, topRight, (255, 0, 0), 2)
                cv.line(img, topRight, bottomRight, (255, 0, 0), 2)
                cv.line(img, bottomRight, bottomLeft, (255, 0, 0), 2)
                cv.line(img, bottomLeft, topLeft, (255, 0, 0), 2)
                # compute and draw the center (x, y)-coordinates of the ArUco
                # marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                cv.circle(img, (cX, cY), 4, (0, 0, 255), -1)
                # draw the ArUco marker ID on the image
                cv.putText(img, str(markerID),
                            (topLeft[0], topLeft[1] - 15), cv.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)
