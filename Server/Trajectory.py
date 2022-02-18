import pickle
import enum
from Configuration import ServerConfig

class RcTrajectoryPoint:
    x = 0
    y = 0
    # velocity
    stopflag = False
    change_point_flag = False

    def __init__(self, x, y, stopflag,change_point_flag):
        self.x = x
        self.y = y
        self.stopflag = stopflag
        self.change_point_flag = change_point_flag

    def __iter__(self):
        for each in self.__dict__.values():
            yield each


class RcTrajectory:
    RcTrajectoryPoints = []
    myReferencePoint = 0
    factorX = 0
    factorY = 0

    def __init__(self, filepath):
        img_width = ServerConfig.getInstance().FrameWidth
        img_height = ServerConfig.getInstance().FrameHeight

        width = ServerConfig.getInstance().TrackWidth
        height = ServerConfig.getInstance().TrackHeight

        self.factorX = img_width / width
        self.factorY = img_height / height

        self.RcTrajectoryPoints = []
        self.myReferencePoint = 0
        with open(filepath, 'rb') as handle:
            path_list = pickle.load(handle)
            for point in path_list:
                if 92*self.factorX > point[0] > 75*self.factorX and 78*self.factorY < point[1] < 153*self.factorY:
                        self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], True,True))
                else:
                        self.RcTrajectoryPoints.append(RcTrajectoryPoint(point[0], point[1], False,True))

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
        try:
            self.__rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')
        except:
            open(r'D:\defaults\parking.trj', 'a').close()
            self.__rc_parking_traj = RcTrajectory(r'D:\defaults\parking.trj')
        try:
            self.__rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')
        except:
            open(r'D:\defaults\normal.trj', 'a').close()
            self.__rc_normal_traj = RcTrajectory(r'D:\defaults\normal.trj')

        self.current_trajectory = self.__rc_normal_traj
        self.parking_button_clicked = False
        self.continue_button_clicked = False
        self.trajectory_changed = False
        self.reference_point = 0

    def get_traj(self):

        if self.parking_button_clicked and self.reference_point.change_point_flag == True :
            self.parking_button_clicked = False
            self.current_trajectory = self.__rc_parking_traj
            print("parking")
        elif self.continue_button_clicked and self.reference_point.change_point_flag == True:
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