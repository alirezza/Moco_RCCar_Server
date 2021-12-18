import socket
from time import sleep

UDPServer_IP = "192.168.4.1"
UDPServer_Port = 8888
msg = bytes("hello", "utf-8")


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.sendto(bytes("test", "utf-8"), (UDPServer_IP, UDPServer_Port))
MAX_ANGLE_LEFT = 147
MAX_ANGLE_RIGHT = -33
angle = MAX_ANGLE_LEFT

clientSocket.sendto(bytes("on", "utf-8"), (UDPServer_IP, UDPServer_Port))
clientSocket.sendto(bytes("255 54", "utf-8"), (UDPServer_IP, UDPServer_Port))
sleep(0.025)
for i in range(55):
    clientSocket.sendto(bytes("115 54", "utf-8"), (UDPServer_IP, UDPServer_Port))
    sleep(0.025)
'''
for i in range(1):
# while True:
    # clientSocket.sendto(bytes(str(180), "utf-8"), (UDPServer_IP, UDPServer_Port))
    clientSocket.sendto(bytes("135 54", "utf-8"), (UDPServer_IP, UDPServer_Port))
    sleep(0.5)
    # clientSocket.sendto(msg, (UDPServer_IP, UDPServer_Port))
    # print("message sent")
    # sleep(5)

    for angle in range(angle, MAX_ANGLE_RIGHT - 1, -1):
        clientSocket.sendto(bytes(str(angle), "utf-8"), (UDPServer_IP, UDPServer_Port))
        print("message sent, angle: ", angle)
        angle += 1
        sleep(0.05)
    for angle in range(angle, MAX_ANGLE_LEFT + 1):
        clientSocket.sendto(bytes(str(angle), "utf-8"), (UDPServer_IP, UDPServer_Port))
        print("message sent, angle: ", angle)
        angle += 1
        sleep(0.05)'''
clientSocket.sendto(bytes("off", "utf-8"), (UDPServer_IP, UDPServer_Port))