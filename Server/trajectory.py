import pickle
import enum


class RcTrajectoryPoint:
    x = 0
    y = 0
    # velocity
    stopflag = False

    # startflag

    def __init__(self, x, y, stopflag=False):
        self.x = x
        self.y = y
        self.stopflag = stopflag

    def __iter__(self):
        for each in self.__dict__.values():
            yield each


class RcTrajectory:
    RcTrajectoryPoints = []
    myReferencePoint = 0

    def __init__(self, filepath):
        self.RcTrajectoryPoints = []
        self.myReferencePoint = 0
        with open(filepath, 'rb') as handle:
            path_list = pickle.load(handle)
            for point in path_list:
                if 180 > point[0] > 130 and 255 < point[1] < 455:
                    self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], True))
                else:
                    self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], False))

    def get_traj(self):
        return self.RcTrajectoryPoints

    def set_ref_point(self, referencePoint):
        self.myReferencePoint = referencePoint


class RcAdaptiveTrajectory(RcTrajectory):
    __rc_parking_traj = 0
    __rc_normal_traj = 0
    parking_button_clicked = False
    continue_button_clicked = False
    trajectory_changed = False
    current_trajectory = 0
    reference_point = 0

    def __init__(self):
        self.__rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')
        self.__rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')
        self.current_trajectory = self.__rc_normal_traj
        self.parking_button_clicked = False
        self.continue_button_clicked = False
        self.trajectory_changed = False
        self.reference_point = RcTrajectoryPoint

    def get_traj(self):

        if self.parking_button_clicked:
            self.parking_button_clicked = False
            self.current_trajectory = self.__rc_parking_traj
            print("parking")
        elif self.continue_button_clicked:
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