import os


class ServerConfig:
    __instance = None

    # Detection
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    filepath = os.path.join(fileDir, r'.\..\Trajs\corner.trj')
    corner_trajectory_adr = filepath

    CamSelect = 1
    # 'http://192.168.223.99:8080/video' for IPCam
    TrackWidth = 138.5  # cm
    TrackHeight = 289  # cm

    # Resolution
    if TrackWidth > TrackHeight:
        FrameWidth = int(640 * TrackWidth / TrackHeight)
        FrameHeight = 640
    elif TrackWidth < TrackHeight:
        FrameWidth = 480
        FrameHeight = int(480 * TrackHeight / TrackWidth)

    # Pixel in cm ratio
    factorX = FrameWidth / TrackWidth
    factorY = FrameHeight / TrackHeight

    # Control
    lookback_n = 1
    lookahead_n = 4

    # Control Parameter
    Preview_Dist_dY_m = 14.005  # Vorausschau Längs
    Preview_Dist_dPsi_m = 18.097  # Vorausschau Winkeldifferenz
    Preview_Dist_K_A_m = 17.083  # Punkt A für Krümmungsberechnung
    Preview_Dist_K_B_m = 19.097  # Punkt B für Krümmungsberechnung

    K_max = 0.0537  # 1/R, Einheit: 1/cm
    K_min = -0.0537  # s.o.

    # Krümmung hat kein Faktor
    lateral_err_dt_gain = 0.2
    lateral_err_dt_coeff = 0.7
    lateral_err_gain = 0.2  # Faktor auf dY_m, Einheit: deg/cm

    heading_err_dt_gain = 0
    heading_err_dt_coeff = 0.7
    heading_err_pt_gain = 0
    heading_err_gain = 0.45  # Faktor auf Winkel

    # WiFi
    UDPServer_IP = "192.168.4.1"  # "192.168.43.110"
    UDPServer_Port = 8888
    MessageDelay = 0.025  # in sek

    # Vehicle
    vehicle_const_speed = 80
    vehicle_angle = 0
    vehicle_curv_factor = 1 / 3
    vehicle_curv_max = 5
    vehicle_curv_min = 0

    vehicle_wheelbase = 9.75 * 1.15  # Radstand, Einheit: cm  # 1.15
    vehicle_steerAngle_MAX = 30  # Einheit: deg
    vehicle_steerAngle_MIN = -30  # s.o.

    steeringAngle_gradient = 70  # Einheit: deg/sek
    sample_time = 0.2  # Abtastzeit (Zeit pro Loop), Einheit: sek

    #GUI information
    vehicle_actual_speed = 0
    vehicle_actual_angle = 0

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
