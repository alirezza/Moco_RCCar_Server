from StateLib import *
from Configuration import ServerConfig
import cv2 as cv
import numpy as np
from numpy.polynomial import polynomial
import socket
import math
from time import sleep


class StateControlCar(State):
    cam = 0
    matrix = 0

    check_i = 5

    img_width = ServerConfig.getInstance().FrameWidth
    img_height = ServerConfig.getInstance().FrameHeight

    # real dimensions (cm)
    width = ServerConfig.getInstance().TrackWidth
    height = ServerConfig.getInstance().TrackHeight

    # factor for px to distance (cm) ratio
    factorX = 0
    factorY = 0

    headingAngle = 0
    headingAngleRad = 0

    carCoordinateX_cm = 0
    carCoordinateY_cm = 0
    lastCoordinate = 0
    lastCoordinate_cm = 0
    lastFigure = 0

    driveCounter = 0

    last_dY_m = 0
    last_dPsi_deg = 0

    finalSteeringAngle_deg = 0
    dSteeringAngle_allowed = 0

    index = 0
    current_path = []
    current_path_cm = []

    carPerspective = []

    dictionary = cv.aruco.Dictionary_get(cv.aruco.DICT_ARUCO_ORIGINAL)
    parameters = cv.aruco.DetectorParameters_create()

    UDPServer_IP = ServerConfig.getInstance().UDPServer_IP
    UDPServer_Port = ServerConfig.getInstance().UDPServer_Port
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self, corner, path):
        self.corner_pts = corner
        self.path_pts = path
        path_pts_toarray = np.array(self.path_pts)
        new_path_pts = np.zeros([path_pts_toarray.shape[0], 3], dtype=float, order='C')
        # for i in range(path_pts_toarray.shape[0]):
        #    new_path_pts[i] = [path_pts_toarray[i][0], path_pts_toarray[i][1], 0]
        # for i in range(path_pts_toarray.shape[0]):
        #    path_pts_toarray[i] = np.matmul(new_path_pts[i], self.matrix)
        self.path_pts_cm = []
        self.control_active = False
        self.control_active_req = False
        self.velocity = ServerConfig.getInstance().vehicle_const_speed

    def next(self):
        return self

    def start_car(self):
        for i in range(3):
            msg = str(0).zfill(3) + " " + str(0).zfill(3)
            self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
            sleep(ServerConfig.getInstance().MessageDelay)

        self.control_active_req = True

    def stop_car(self):
        msg = str(0).zfill(3) + " " + str(0).zfill(3)
        self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
        sleep(ServerConfig.getInstance().MessageDelay)
        self.control_active_req = False

    def set_velocity(self, v):
        self.velocity = int(v)

    def run(self):

        # 1 Transformiere Bild
        ret, new_frame = self.cam.read()

        if ret:
            track_img = cv.warpPerspective(new_frame, self.matrix, (self.img_width, self.img_height))
            # track_img = cv.warpPerspective(new_frame,self.matrix,900,1080)
            carMarkerCorners, carMarkerIds, rejectedCandidates = cv.aruco.detectMarkers(track_img, self.dictionary,
                                                                                        parameters=self.parameters)
            '''for point in self.path_pts:
                cv.circle(track_img, (point[0], point[1]), 4, (0, 255, 255), -1)
            cv.polylines(track_img, [np.array(self.path_pts)], True, (0, 255, 0), 3)'''

            # 2 Ermittle Position/Winkel Fahrzeug
            # if marker is detected
            try:
                if len(carMarkerIds.tolist()) == 1:
                    if carMarkerIds == 21:
                        for (carCorner, carID) in zip(carMarkerCorners, carMarkerIds):

                            carMarkerCorners = carCorner.reshape(4, 2)

                            # get coordinates
                            topLeft, topRight, bottomRight, bottomLeft = carMarkerCorners

                            # draw car middle point
                            carCoordinateX = int((topLeft[0] + bottomRight[0]) / 2.0)
                            carCoordinateY = int((topLeft[1] + bottomRight[1]) / 2.0)
                            self.lastCoordinate = (carCoordinateX, carCoordinateY)
                            self.carCoordinateX_cm = carCoordinateX / self.factorX
                            self.carCoordinateY_cm = carCoordinateY / self.factorY
                            self.lastCoordinate_cm = (self.carCoordinateX_cm, self.carCoordinateY_cm)
                            cv.circle(track_img, (carCoordinateX, carCoordinateY), 4, (0, 0, 255), -1)
                            '''cv.putText(track_img, f"x: {carCoordinateX}, y: {carCoordinateY}",
                                       (carCoordinateX, carCoordinateY - 15),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)'''

                            # draw car figure
                            carFigure = [[int((topLeft[0] + topRight[0]) / 2.0), int((topLeft[1] + topRight[1]) / 2.0)],
                                         [int(bottomLeft[0]), int(bottomLeft[1])],
                                         [int(bottomRight[0]), int(bottomRight[1])]]
                            self.lastFigure = carFigure

                            cv.polylines(track_img, [np.array(self.lastFigure)], True, (255, 0, 0), 3)
                            cv.polylines(track_img, [np.array(self.path_pts)], True, (0, 255, 0), 3)

                            # calculate heading angle
                            if not (topLeft[0] == bottomLeft[0] and topLeft[1] == bottomLeft[1]):

                                self.headingAngleRad = np.arctan2(bottomRight[0] - topRight[0],
                                                                  topRight[1] - bottomRight[1]) + math.pi / 2

                                if self.headingAngleRad < 0:
                                    self.headingAngleRad = (self.headingAngleRad + 2 * math.pi)

                                self.headingAngle = round(np.rad2deg(self.headingAngleRad), 2)

            # if no marker is detected
            except AttributeError:
                if self.lastFigure:
                    cv.circle(track_img, self.lastCoordinate, 4, (0, 255, 255), -1)
                    cv.polylines(track_img, [np.array(self.lastFigure)], True, (0, 0, 255), 3)

            # print(f"coordinates - x, y: {self.carCoordinateX_cm}cm, {self.carCoordinateY_cm}cm")
            # print(f"heading angle: {self.headingAngle}")
            # print(f"heading angle rad: {self.headingAngleRad}")

            # 3 Ermittle Referenzpunkt (nähester Punkt) auf Pfad
            if self.carCoordinateX_cm > 0 and self.carCoordinateY_cm > 0:
                if (not self.control_active) or (self.check_i == 0):
                    self.check_i = 10
                    deltaCoordinate = [
                        (path_pt[0] - self.carCoordinateX_cm, path_pt[1] - self.carCoordinateY_cm) for
                        path_pt in self.path_pts_cm]
                    deltaDistance = [round(pow(distance[0], 2) + pow(distance[1], 2), 2) for distance in
                                     deltaCoordinate]
                    self.index = deltaDistance.index(min(deltaDistance))
                    print(self.index)
                else:
                    self.check_i -= 1
                    print("before " + str(self.index))
                    max_index = self.path_pts_cm.index(self.path_pts_cm[-1])
                    paths = []
                    for i in range(10):
                        paths.append(self.path_pts_cm[(i + self.index) % max_index])
                    deltaCoordinate = [
                        (path_pt[0] - self.carCoordinateX_cm, path_pt[1] - self.carCoordinateY_cm) for
                        path_pt in paths]
                    deltaDistance = [round(pow(distance[0], 2) + pow(distance[1], 2), 2) for distance in
                                     deltaCoordinate]
                    temp_index = deltaDistance.index(min(deltaDistance))
                    self.index = temp_index + self.index
                    print("after " + str(self.index))

                # 4 Punkte vor und nach Referenzpunkt
                start_index = self.index - ServerConfig.getInstance().lookback_n
                if start_index < 0:
                    start_index = len(self.path_pts) + start_index
                if start_index + 1 + ServerConfig.getInstance().lookahead_n > len(self.path_pts) - 1:
                    self.current_path = self.path_pts[start_index:len(self.path_pts)] + self.path_pts[
                                                                                        0:ServerConfig.getInstance().lookahead_n - (
                                                                                                len(self.path_pts) - 1 - self.index)]
                    self.current_path_cm = self.path_pts_cm[start_index:len(self.path_pts)] + self.path_pts_cm[
                                                                                              0:ServerConfig.getInstance().lookahead_n - (
                                                                                                      len(self.path_pts) - 1 - self.index)]
                else:
                    self.current_path = self.path_pts[
                                        start_index:self.index + ServerConfig.getInstance().lookahead_n + 1]
                    self.current_path_cm = self.path_pts_cm[
                                           start_index:self.index + ServerConfig.getInstance().lookahead_n + 1]
                # print(f'current path: {self.current_path}')
                '''for p_x, p_y in self.current_path:
                    cv.circle(track_img, (p_x, p_y), 10, (255, 0, 0),
                              -1)
                cv.circle(track_img, (self.path_pts[start_index][0], self.path_pts[start_index][1]), 10, (0, 0, 0), -1)
                cv.circle(track_img, (self.path_pts[self.index][0], self.path_pts[self.index][1]), 10, (0, 0, 255), -1)'''

                # 5 Berechne Abstände von Fahrzeug zu nächsten Punkten
                distance_to_vec = []
                for x, y in self.current_path_cm:
                    # print(f'x, y - path point: {x, y}')
                    x_diff, y_diff = x - self.lastCoordinate_cm[0], y - self.lastCoordinate_cm[1]
                    # print(f'x_diff, y_diff: {x_diff, y_diff}')
                    # 6 Transformiere Koordinatensystem zu Fahrzeugsicht
                    distance_to_vec.append([round(x_diff, 2) * math.cos(self.headingAngleRad) + round(y_diff,
                                                                                                      2) * math.sin(
                        self.headingAngleRad), -1 * (round(x_diff, 2) * math.sin(self.headingAngleRad) - round(y_diff,
                                                                                                               2) * math.cos(
                        self.headingAngleRad))])
                # print("dis_to_vec_list: ", [i[0] for i in distance_to_vec], [i[1] for i in distance_to_vec])
                # print("dis_to_vec_list: ", distance_to_vec)
                # print("index : ", self.index, "start_index: ", start_index)
                cv.putText(track_img,
                           f"x: {round(distance_to_vec[ServerConfig.getInstance().lookback_n][0], 2)} cm, y: {round(distance_to_vec[ServerConfig.getInstance().lookback_n][1], 2)} cm",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 15),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                # 6 Berechne Querablagefehler
                # Fzggeschwindigkeit (längs) noch nicht berücksichtigt
                coeffs = np.polyfit([i[0] for i in distance_to_vec], [i[1] for i in distance_to_vec],
                                    2)  # bilde Polynom aus Abstand zu Punkten
                # print(f'coeff: {coeffs}')
                dY_m = -1 * np.polyval(coeffs,
                                       ServerConfig.getInstance().Preview_Dist_dY_m)  # Querablagefehler, vielleicht Vorzeichen umdrehen
                cv.putText(track_img,
                           f"dY_m: {round(dY_m, 2)} cm",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 30),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # 7 Berechne Winkeldifferenz & Krümmung
                coeffs_flipped = np.flip(coeffs)
                # print(f'flipped: {coeffs_flipped}')
                coeffsPsi = np.polynomial.polynomial.polyder(coeffs_flipped, 1)  # bilde Abteilungsfunktion
                # print(f'ableitungscoeff: {coeffsPsi}')
                coeffsPsi_flipped = np.flip(coeffsPsi)
                dPsi_deg = -1 * np.rad2deg(math.atan(np.polyval(coeffsPsi_flipped,
                                                                ServerConfig.getInstance().Preview_Dist_dPsi_m)))  # Winkeldifferenz Fahrzeug zur Tangente
                dPsi_radA = -1 * (
                    np.arctan(np.polyval(coeffsPsi_flipped, ServerConfig.getInstance().Preview_Dist_K_A_m)))
                dPsi_radB = -1 * (
                    np.arctan(np.polyval(coeffsPsi_flipped, ServerConfig.getInstance().Preview_Dist_K_B_m)))

                K_minv = (dPsi_radB - dPsi_radA) / (
                        ServerConfig.getInstance().Preview_Dist_K_B_m - ServerConfig.getInstance().Preview_Dist_K_A_m)  # Krümmung
                # Einheit, K: rad / cm
                # print(f'dY: {dY_m}, dPsi_deg: {dPsi_deg}, K_minv: {K_minv}')

                # 8 Berechne Lenkwinkel
                if K_minv > ServerConfig.getInstance().K_max:
                    K_minv = ServerConfig.getInstance().K_max
                if K_minv < ServerConfig.getInstance().K_min:
                    K_minv = ServerConfig.getInstance().K_min

                curvature_steerAngle_rad = K_minv * ServerConfig.getInstance().vehicle_wheelbase
                curvature_steerAngle_deg = np.rad2deg(curvature_steerAngle_rad)

                # dt1 filter for lateral error control ###
                error = dY_m - self.last_dY_m
                lateral_error_angle_deg_dt1 = error * ServerConfig.getInstance().lateral_err_dt_gain
                self.last_dY_m = error * ServerConfig.getInstance().lateral_err_dt_coeff + self.last_dY_m
                ###

                lateral_error_angle_deg = dY_m * ServerConfig.getInstance().lateral_err_gain + lateral_error_angle_deg_dt1

                # dt1, pt1 filter for heading error control ###
                error = dPsi_deg - self.last_dPsi_deg
                heading_error_angle_deg_dt1 = error * ServerConfig.getInstance().heading_err_dt_gain
                self.last_dPsi_deg = error * ServerConfig.getInstance().heading_err_dt_coeff + self.last_dPsi_deg
                heading_error_angle_deg_pt1 = self.last_dPsi_deg * ServerConfig.getInstance().heading_err_pt_gain
                ###

                heading_error_angle_deg = dPsi_deg * ServerConfig.getInstance().heading_err_gain + heading_error_angle_deg_dt1 + heading_error_angle_deg_pt1

                steerAngle_req = curvature_steerAngle_deg + lateral_error_angle_deg + heading_error_angle_deg
                if steerAngle_req > ServerConfig.getInstance().vehicle_steerAngle_MAX:
                    steerAngle_req = ServerConfig.getInstance().vehicle_steerAngle_MAX
                if steerAngle_req < ServerConfig.getInstance().vehicle_steerAngle_MIN:
                    steerAngle_req = ServerConfig.getInstance().vehicle_steerAngle_MIN

                diff_steerAngle = steerAngle_req - self.finalSteeringAngle_deg
                if abs(diff_steerAngle) > self.dSteeringAngle_allowed:
                    self.finalSteeringAngle_deg = self.finalSteeringAngle_deg + (
                            self.dSteeringAngle_allowed * np.sign(diff_steerAngle))
                else:
                    self.finalSteeringAngle_deg = steerAngle_req
                cv.putText(track_img,
                           f"curvature_steerAngle_deg: {round(curvature_steerAngle_deg, 2)}",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 45),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv.putText(track_img,
                           f"lateral_error_angle_deg: {round(lateral_error_angle_deg, 2)}",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 60),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv.putText(track_img,
                           f"heading_error_angle_deg: {round(heading_error_angle_deg, 2)}",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 75),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv.putText(track_img,
                           f"finalSteeringAngle_deg: {round(self.finalSteeringAngle_deg, 2)}",
                           (self.lastCoordinate[0] + 20, self.lastCoordinate[1] - 90),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # print(f'steeringAngle: {self.finalSteeringAngle_deg}')
                # Trajektorie printen
                # print(f'coeffs: {coeffs}')
                # coeffs_px = [i * self.factor for i in coeffs]

                coeffs_px = np.polyfit([i[0] for i in self.current_path], [i[1] for i in self.current_path],
                                       2)  # bilde Polynom aus Abstand zu Punkten
                cv_pts_y = [np.polyval(coeffs_px, i[0]) for i in self.current_path]
                cv_pts = []
                for i in range(len(self.current_path)):
                    cv_pts.append([self.current_path[i][0], int(cv_pts_y[i])])
                # print(cv_pts)
                for i in cv_pts:
                    cv.circle(track_img, i, 5, (255, 0, 0))
                cv.polylines(track_img, [np.array(cv_pts)], False, (0, 0, 255), 1)

                # Activate/Deactivate Control
                if self.control_active_req is not self.control_active:
                    self.control_active = self.control_active_req
                    # sende Anfahrreq
                    if self.control_active_req:
                        msg = str(200).zfill(3) + " " + str(0).zfill(3)
                        self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                        sleep(ServerConfig.getInstance().MessageDelay)
                    # sende Stopreq
                    else:
                        msg = str(0).zfill(3) + " " + str(0).zfill(3)
                        self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                        sleep(ServerConfig.getInstance().MessageDelay)

                    # msg = "255 " + str(int(-self.finalSteeringAngle_deg))
                    # self.clientSocket.sendto(bytes(str(msg), "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                    # sleep(ServerConfig.getInstance().MessageDelay)
                elif self.control_active:
                    # 9 Sende Daten (Querablagefehler, Winkeldifferenz, Krümmung)sg = str(dY_m, dPsi_rad/dPsi_deg, K_minv)  # "Winkel, Geschwindigkeit" muss formatiert sein
                    # accel = ServerConfig.getInstance().vehicle_speed + int(
                    #    pow(abs(self.finalSteeringAngle_deg) * 0.1, 2.5))
                    accel = self.velocity
                    angle = self.finalSteeringAngle_deg

                    if (
                            abs(angle) * ServerConfig.getInstance().vehicle_curv_factor) < ServerConfig.getInstance().vehicle_curv_min:
                        accel += ServerConfig.getInstance().vehicle_curv_min
                    if (
                            abs(angle) * ServerConfig.getInstance().vehicle_curv_factor) > ServerConfig.getInstance().vehicle_curv_max:
                        accel += ServerConfig.getInstance().vehicle_curv_max
                    else:
                        accel += (abs(angle) * ServerConfig.getInstance().vehicle_curv_factor)

                    accel = math.trunc(accel)
                    angle = math.trunc(angle)
                    # print(f'accel: {accel}')
                    # print(f'angle: {angle}')

                    msg = str(accel).zfill(3) + " " + str(angle).zfill(3)

                    # msg = str(accel).zfill(3) + " " + str(angle).zfill(3)
                    self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                    sleep(ServerConfig.getInstance().MessageDelay)

                    # accel = ServerConfig.getInstance().vehicle_const_speed + int(abs(self.finalSteeringAngle_deg) * 0.3)
                    # accel = 100
                    # print(accel)
                    # accel = self.velocity + int(pow(abs(self.finalSteeringAngle_deg) * 0.2, 2))
                    # print(self.velocity)
                    # print(f'accel: {accel}')
                    # msg = "000" + " " + str(int(-self.finalSteeringAngle_deg))
                    # msg = str(accel) + " " + str(int(-self.finalSteeringAngle_deg))
                    # self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                    # sleep(ServerConfig.getInstance().MessageDelay)

                    '''msg = str(int(ServerConfig.getInstance().vehicle_const_speed + 0.25 * abs(self.finalSteeringAngle_deg))) + " " + str(int(-self.finalSteeringAngle_deg))
                    print(f'msg: {msg}')
                    self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
                    sleep(ServerConfig.getInstance().MessageDelay)'''

            cv.imshow('Track Record', track_img)
            k = cv.waitKey(20) & 0xFF

    def on_enter(self):

        print("Enter Control State")

        self.cam = cv.VideoCapture(ServerConfig.getInstance().CamSelect)
        self.cam.set(cv.CAP_PROP_FRAME_WIDTH, ServerConfig.getInstance().FrameWidth)
        self.cam.set(cv.CAP_PROP_FRAME_HEIGHT, ServerConfig.getInstance().FrameHeight)

        if not self.cam.isOpened():
            print("Error opening video stream or file")

        pts1 = np.asarray(self.corner_pts, dtype=np.float32)
        pts2 = np.float32([[0, 0], [self.img_width, 0], [0, self.img_height], [self.img_width, self.img_height]])
        self.matrix = cv.getPerspectiveTransform(pts1, pts2)

        # factor for px to distance (cm) ratio
        self.factorX = self.img_width / self.width
        self.factorY = self.img_height / self.height

        self.dSteeringAngle_allowed = ServerConfig.getInstance().steeringAngle_gradient * ServerConfig.getInstance().sample_time

        for path_point in self.path_pts:
            self.path_pts_cm.append([path_point[0] / self.factorX, path_point[1] / self.factorY])
        print(self.path_pts_cm)

    def on_leave(self):
        msg = str(0).zfill(3) + " " + str(0).zfill(3)
        self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
        sleep(ServerConfig.getInstance().MessageDelay)
        cv.destroyAllWindows()
        self.cam.release()
        print("Leaving Control Car State")
