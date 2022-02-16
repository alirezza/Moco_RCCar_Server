import pickle
import State_PathDetect as pathDetection

parkingPoint = 0
startCruisePoint = 20
import enum


class RcTrajectoryPoint:
    def __init__(self, x, y, i):
        x = x
        y = y

    i = 0
    x = 0
    y = 0
    # velocity
    # stopflag
    # startflag


class RcTrajectory:
    RcTrajectoryPoints = []
    myReferencePoint = 0

    def __init__(self, filepath):
        with open(filepath, 'r+b') as handle:
            path_list = pickle.load(handle)
            i = 0
            for point in path_list:
                self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1],i))
                i += 1

    def get_traj(self):
        return self.RcTrajectoryPoints

    def set_ref_point(self, referencePoint):
        self.myReferencePoint = referencePoint


class RcAdaptiveTrajectory(RcTrajectory):
    rc_normal_traj = RcTrajectory(r'D:\defaultPaths\normal.trj')
    rc_parking_traj = RcTrajectory(r'D:\defaultPaths\parking.trj')

    current_trajectory = rc_normal_traj
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

        if RcAdaptiveTrajectory.check_event(self.reference_point) == self.Events.parking:
            self.current_trajectory = self.rc_parking_traj
        elif RcAdaptiveTrajectory.check_event(self.reference_point) == self.Events.cruising:
            self.current_trajectory = self.rc_normal_traj

        return self.current_trajectory

    def set_ref_point(self, reference_point):
        self.reference_point = reference_point
