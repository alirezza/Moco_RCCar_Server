class ServerConfig:
    __instance = None

    # WiFi
    UDPServer_IP = "192.168.4.1"
    UDPServer_Port = 8888
    MessageDelay = 0.025  # in sek

    # Vehicle
    vehicle_speed = 135
    testingsteeringangle = 37

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ServerConfig.__instance is None:
            ServerConfig()
        return ServerConfig.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ServerConfig.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ServerConfig.__instance = self
