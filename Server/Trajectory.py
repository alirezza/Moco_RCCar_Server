import pickle
import enum
from Configuration import ServerConfig


class RcTrajectoryPoint:
    x = 0
    y = 0
    # velocity
    stopflag = False
    change_point_flag = False

    def __init__(self, x, y, stopflag, change_point_flag):
        self.x = x
        self.y = y
        self.stopflag = stopflag  # true if point in parkingarea
        self.change_point_flag = change_point_flag  # true if point in changpatharea

    def __iter__(self):
        for each in self.__dict__.values():
            yield each


class RcTrajectory:
    RcTrajectoryPoints = []
    myReferencePoint = 0
    factorX = 0
    factorY = 0

    def __init__(self, path):
        # for lock in path
        if isinstance(path, list):
            self.RcTrajectoryPoints = []
            self.myReferencePoint = 0
            for point in path:
                self.RcTrajectoryPoints.append(
                    RcTrajectoryPoint(point[0], point[1], isStopPoint(point), isChangePoint(point)))
        else:
            # if trj is a .trj file
            self.RcTrajectoryPoints = []
            self.myReferencePoint = 0
            with open(path, 'rb') as handle:
                path_list = pickle.load(handle)
                for point in path_list:
                    self.RcTrajectoryPoints.append(
                        RcTrajectoryPoint(point[0], point[1], isStopPoint(point), isChangePoint(point)))

    def get_traj(self):
        return self.RcTrajectoryPoints

    def set_ref_point(self, referencePoint):
        self.myReferencePoint = referencePoint


class RcAdaptiveTrajectory():
    __rc_parking_traj = 0
    __rc_normal_traj = 0
    parking_button_clicked = False
    continue_button_clicked = False
    trajectory_changed = False
    current_trajectory = 0
    reference_point = 0

    def __init__(self):
        try:
            self.__rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')
        except FileNotFoundError and FileExistsError:
            open(r'D:\defaults\parking.trj', 'a').close()
            self.__rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')
        try:
            self.__rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')
        except FileNotFoundError and FileExistsError:
            open(r'D:\defaults\normal.trj', 'a').close()
            self.__rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')

        self.current_trajectory = self.__rc_normal_traj
        self.parking_button_clicked = False
        self.continue_button_clicked = False
        self.trajectory_changed = False
        var = self.reference_point

    def get_traj(self):

        if self.parking_button_clicked and self.reference_point.change_point_flag:
            self.parking_button_clicked = False
            self.current_trajectory = self.__rc_parking_traj
            print("parking")
        elif self.continue_button_clicked and self.reference_point.change_point_flag:
            self.continue_button_clicked = False
            self.current_trajectory = self.__rc_normal_traj
            print("continue")

        return self.current_trajectory.get_traj()

    def set_ref_point(self, reference_point):
        # print(reference_point.stopflag)
        self.reference_point = reference_point

    def get_current_trj(self):
        return self.current_trajectory

    def changeDir(self):
        self.__rc_normal_traj.get_traj().reverse()
        self.__rc_parking_traj.get_traj().reverse()
        self.current_trajectory.get_traj().reverse()


def isStopPoint(point):
    factorX = ServerConfig.getInstance().factorX
    factorY = ServerConfig.getInstance().factorY
    # check if pointcoordinates are in the parking area
    if 92 * factorX > point[0] > 75 * factorX and 78 * factorY < point[1] < 153 * factorY:
        return True
    else:
        return False


def isChangePoint(point):
    factorX = ServerConfig.getInstance().factorX
    factorY = ServerConfig.getInstance().factorY
    # check if pointcoordinates are in the changepath area
    if 40 * factorX > point[0] > 18 * factorX and 60 * factorY < point[1] < 80 * factorY:
        print("is a Change Point")
        print(point)
        return True

    else:
        return False
