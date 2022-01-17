import socket
from time import sleep
import cv2 as cv
from Configuration import ServerConfig
from StateLib import *


class StateControlCar(State):
    UDPServer_IP = ServerConfig.getInstance().UDPServer_IP
    UDPServer_Port = ServerConfig.getInstance().UDPServer_Port
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __init__(self):
        self.control_active = False
        self.control_active_req = False
        self.velocity = 170
        self.angle = 107

    def next(self):
        return self

    def start_car(self):
        self.control_active_req = True

    def stop_car(self):
        self.control_active_req = False

    def set_velocity(self, v):
        self.velocity = v

    def get_velocity(self):
        return self.velocity

    def set_angle(self, v):
        self.angle = v

    def run(self):

        if self.control_active_req is not self.control_active:
            self.control_active = self.control_active_req
            if self.control_active:
                msg = "170 107"
                for i in range(10):
                    self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))

            # send Anfahrreq
            else:
                msg = "000 107"
                self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))

        elif self.control_active:
            # 9 Sende Daten (Querablagefehler, Winkeldifferenz, Krümmung)sg = str(dY_m, dPsi_rad/dPsi_deg, K_minv)  # "Winkel, Geschwindigkeit" muss formatiert sein

            accel = self.velocity
            angle = self.angle

            print(f'accel: {accel}')
            print(f'angle: {angle}')

            msg = str(accel).zfill(3) + " " + str(angle).zfill(3)
            self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
            sleep(ServerConfig.getInstance().MessageDelay)

    def on_enter(self):

        print("Enter Control State")

    def on_leave(self):
        #msg = "off"
        msg = "000 107"
        self.clientSocket.sendto(bytes(msg, "utf-8"), (self.UDPServer_IP, self.UDPServer_Port))
        print("Leaving Control Car State")
