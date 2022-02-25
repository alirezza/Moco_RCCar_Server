import os
import threading

from PySide6.QtCore import *
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QLabel, QFileDialog, QSlider, QWidget, \
    QGroupBox, QTabWidget, QDialogButtonBox

from Configuration import ServerConfig
from StateLib import *
from State_ControlCar import StateControlCar
from State_CornerDetection import StateCornerDetection
from State_PathDetect import StatePathDetect


class LogicLoop:
    killLoop = False

    def __init__(self):
        self.myStateMachine = StateMachine(StateCornerDetection())
        self.killLoop = False

    def loop(self):
        while not self.killLoop:
            self.myStateMachine.run()

        self.myStateMachine.currentState.on_leave()
        print("Logic Loop Ended")

@Slot()
def restart_state_machine():
    myLogicThread.myStateMachine.force_next_state(StateCornerDetection())
    print("Restart")


@Slot()
def create_path():
    if isinstance(myLogicThread.myStateMachine.currentState, StatePathDetect):
        myLogicThread.myStateMachine.currentState.set_use_path(True)
        print("Try to create path")


@Slot()
def clear_path():
    if isinstance(myLogicThread.myStateMachine.currentState, StatePathDetect):
        myLogicThread.myStateMachine.currentState.set_use_path(False)


@Slot()
def load_path(widget):
    if isinstance(myLogicThread.myStateMachine.currentState, StatePathDetect):
        LoadDialog = QFileDialog.getOpenFileName(widget, 'Open file', 'd:\\', "TrajectoryFiles (*.trj)")
        # print(LoadDialog)
        if LoadDialog[0] != '':
            myLogicThread.myStateMachine.currentState.load_trajectory(LoadDialog[0])


@Slot()
def save_path(widget):
    if isinstance(myLogicThread.myStateMachine.currentState, StatePathDetect):
        SaveDialog = QFileDialog.getSaveFileName(widget, 'Save file', 'd:\\', "TrajectoryFiles (*.trj)")
        if SaveDialog[0] != '':
            myLogicThread.myStateMachine.currentState.save_trajectory(SaveDialog[0])


@Slot()
def start_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.start_car()


@Slot()
def stop_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.stop_car()


@Slot()
def park_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.continue_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.half_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.parking_button_clicked = True
        myLogicThread.myStateMachine.currentState.car_park()


@Slot()
def continue_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.parking_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.half_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.continue_button_clicked = True
        myLogicThread.myStateMachine.currentState.car_continue()


def half_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.parking_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.continue_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.half_button_clicked = True
        myLogicThread.myStateMachine.currentState.car_half()


@Slot()
def set_velocity(vel):
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.set_velocity(vel)
    print(vel)


@Slot()
def newPath():
    myLogicThread.myStateMachine.force_next_state(StatePathDetect())


@Slot()
def resetCorner():
    os.remove(StateCornerDetection.corner_trajectory_adr)
    print("old corner trj removed")
    restart_state_machine()


@Slot()
def changeDir():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.changeDir()
        myLogicThread.myStateMachine.currentState.path_pts_cm.reverse()
        print("Direction changed")


class TabDialog(QDialog):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        tab_widget = QTabWidget()
        tab_widget.addTab(MainTab(self), "Main")
        tab_widget.addTab(PathTab(self), "Path")
        tab_widget.addTab(SettingTab(self), "Applications")

        button_box = QDialogButtonBox(
            QDialogButtonBox.Cancel
        )

        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)
        self.setWindowTitle("RC Car")
        self.resize(300, 500)


class MainTab(QWidget):
    speed = 0
    angle = 0
    def updateValues(self, speed, angle):
        self.statusText_actualspeed.setText(str(speed))
        self.statusText_actualangle.setText(str(angle))

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        main_group = QGroupBox("Main")
        self.start_button = QPushButton("Start Car")
        self.stop_car = QPushButton("Stop Car")
        manoeuvre_group = QGroupBox("Manoeuvres")
        self.park_button = QPushButton("Park")
        self.continue_button = QPushButton("Continue")
        self.half_button = QPushButton("Short round")
        information_gruop = QGroupBox("Information")
        self.statusText_speed = QLabel("Speed: ")
        self.statusText_actualspeed = QLabel("0")
        self.statusText_angle = QLabel("Steering angle: ")
        self.statusText_actualangle = QLabel("0")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_car)
        main_group.setLayout(main_layout)

        manoeuvre_layout = QVBoxLayout()
        manoeuvre_layout.addWidget(self.park_button)
        manoeuvre_layout.addWidget(self.continue_button)
        manoeuvre_layout.addWidget(self.half_button)
        manoeuvre_group.setLayout(manoeuvre_layout)

        information_layout = QVBoxLayout()
        information_layout.addWidget(self.statusText_speed)
        information_layout.addWidget(self.statusText_actualspeed)
        information_layout.addWidget(self.statusText_angle)
        information_layout.addWidget(self.statusText_actualangle)
        information_gruop.setLayout(information_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_group)
        main_layout.addWidget(manoeuvre_group)
        main_layout.addWidget(information_gruop)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

        self.start_button.clicked.connect(start_car)
        self.stop_car.clicked.connect(stop_car)
        self.park_button.clicked.connect(park_car)
        self.continue_button.clicked.connect(continue_car)
        self.half_button.clicked.connect(half_car)


class PathTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        path_group = QGroupBox("Path")

        self.lock_in_button = QPushButton("Lock In Path")
        self.clear_button = QPushButton("Clear Path")
        self.load_button = QPushButton("Load Path")
        self.save_button = QPushButton("Save Path")
        self.create_path_button = QPushButton("Create new Path")

        path_layout = QVBoxLayout()
        path_layout.addWidget(self.create_path_button)
        path_layout.addWidget(self.lock_in_button)
        path_layout.addWidget(self.clear_button)
        path_layout.addWidget(self.save_button)
        path_layout.addWidget(self.load_button)
        path_group.setLayout(path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(path_group)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.lock_in_button.clicked.connect(create_path)
        self.clear_button.clicked.connect(clear_path)
        self.load_button.clicked.connect(lambda: load_path(self))
        self.save_button.clicked.connect(lambda: save_path(self))
        self.create_path_button.clicked.connect(newPath)


class SettingTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        setting_group = QGroupBox("Setting")

        self.reset_button = QPushButton("Reset State Machine")
        self.dir_change_button = QPushButton("Change Direction")
        self.reset_corners_button = QPushButton("Reset Corners")
        self.speed_text = QLabel("Speed")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 170)
        self.speed_slider.setTickInterval(5)
        self.speed_slider.setValue(ServerConfig.getInstance().vehicle_const_speed)

        setting_layout = QVBoxLayout()
        setting_layout.addWidget(self.reset_button)
        setting_layout.addWidget(self.dir_change_button)
        setting_layout.addWidget(self.reset_corners_button)
        setting_layout.addWidget(self.speed_text)
        setting_layout.addWidget(self.speed_slider)
        setting_group.setLayout(setting_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(setting_group)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.reset_corners_button.clicked.connect(resetCorner)
        self.dir_change_button.clicked.connect(changeDir)
        self.reset_button.clicked.connect(restart_state_machine)


# Create the Qt Application
app = QApplication([])

# Create Thread that runs in parallel to the gui
myLogicThread = LogicLoop()
LogicThread = threading.Thread(target=myLogicThread.loop, args=())

myDialog = TabDialog()
myDialog.show()

LogicThread.start()
app.exec()

# If GUI is closed tell thread to close
myLogicThread.killLoop = True
