import pickle
import enum

parkingPoint = 0
startCruisePoint = 20


class RcTrajectoryPoint:
    def __init__(self, x, y, i, stopflag=False):
        self.x = x
        self.y = y
        self.i = i
        self.stopflag = stopflag

    def __iter__(self):
        for each in self.__dict__.values():
            yield each

    i = 0
    x = 0
    y = 0
    # velocity
    stopflag = False
    # startflag


class RcTrajectory:
    RcTrajectoryPoints = []
    myReferencePoint = RcTrajectoryPoint

    def __init__(self, filepath):
        with open(filepath, 'r+b') as handle:
            path_list = pickle.load(handle)
            i = 0
            for point in path_list:
                if 42 > point[0] > 39 and 72 < point[1] < 133:
                    self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], i, True))
                else:
                    self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], i, False))
                i += 1

    def get_traj(self):
        return self.RcTrajectoryPoints

    def set_ref_point(self, referencePoint):
        self.myReferencePoint = referencePoint


class RcAdaptiveTrajectory(RcTrajectory):
    def __init__(self):
        self.current_trajectory = self.__rc_normal_traj
        self.parking_button_clicked = False
        self.continue_button_clicked = False
        self.trajectory_changed = False

    __rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')
    __rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')

    current_trajectory = RcTrajectory
    reference_point = RcTrajectoryPoint

    parking_button_clicked = False
    continue_button_clicked = False
    trajectory_changed = False

    class Events(enum.Enum):
        parking = 0
        cruising = 1
        noChange = 2

    def check_event(self, reference_point):
        if self.parking_button_clicked and reference_point.i == parkingPoint:
            self.parking_button_clicked = False
            return self.Events.parking
        if self.continue_button_clicked and reference_point.i == startCruisePoint:
            self.continue_button_clicked = False
            return self.Events.cruising
        else:
            return self.Events.noChange

    def get_traj(self):

        #if RcAdaptiveTrajectory.check_event(self.reference_point) == self.Events.parking:
            #self.current_trajectory = self.__rc_parking_traj
        #elif RcAdaptiveTrajectory.check_event(self.reference_point) == self.Events.cruising:
        self.current_trajectory = self.__rc_normal_traj

        return self.current_trajectory

    def set_ref_point(self, reference_point):
        self.reference_point = reference_point
