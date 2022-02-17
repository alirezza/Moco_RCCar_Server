import os
import sys

from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QLabel, QFileDialog, QSlider
from PySide6.QtCore import *
import threading
import time

import trajectory
from State_ControlCar import StateControlCar
from State_PathDetect import StatePathDetect
from StateLib import *
from State_CornerDetection import StateCornerDetection
from Configuration import ServerConfig


class LogicLoop:
    killLoop = False

    def __init__(self):
        self.myStateMachine = StateMachine(StateCornerDetection())
        self.killLoop = False

    def loop(self):
        while self.killLoop == False:
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
    trajectory.RcAdaptiveTrajectory.parking_button_clicked = True
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.car_park()


@Slot()
def continue_car():
    trajectory.RcAdaptiveTrajectory.continue_button_clicked = True
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.car_continue()

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


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.button1 = QPushButton("Reset State Machine")
        self.button2 = QPushButton("Lock In Path")
        self.button3 = QPushButton("Clear Path")
        self.button4 = QPushButton("Load Path")
        self.button5 = QPushButton("Save Path")
        self.button6 = QPushButton("Start Car")
        self.button7 = QPushButton("Stop Car")
        self.button8 = QPushButton("Park")
        self.button9 = QPushButton("Continue")
        self.button10 = QPushButton("Reset Corners")
        self.button11 = QPushButton("Create new Path")
        self.slider1 = QSlider(Qt.Horizontal)
        self.statusText = QLabel("Status Label")

        self.slider1.setRange(0, 150)
        self.slider1.setTickInterval(1)
        self.slider1.setValue(ServerConfig.getInstance().vehicle_const_speed)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button6)
        layout.addWidget(self.button7)
        layout.addWidget(self.button8)
        layout.addWidget(self.button9)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button5)
        layout.addWidget(self.button4)
        layout.addWidget(self.button10)
        layout.addWidget(self.button11)
        layout.addWidget(self.statusText)
        layout.addWidget(self.slider1)

        # Set dialog layout
        self.setLayout(layout)


# Create the Qt Application
app = QApplication([])

# Create Thread that runs in parallel to the gui
myLogicThread = LogicLoop()
LogicThread = threading.Thread(target=myLogicThread.loop, args=())

myDialog = Form()
myDialog.button1.clicked.connect(restart_state_machine)
myDialog.button2.clicked.connect(create_path)
myDialog.button3.clicked.connect(clear_path)
myDialog.button4.clicked.connect(lambda: load_path(myDialog))
myDialog.button5.clicked.connect(lambda: save_path(myDialog))
myDialog.button6.clicked.connect(start_car)
myDialog.button7.clicked.connect(stop_car)
myDialog.button8.clicked.connect(park_car)
myDialog.button9.clicked.connect(continue_car)
myDialog.button10.clicked.connect(resetCorner)
myDialog.button11.clicked.connect(newPath)
myDialog.slider1.valueChanged.connect(lambda: set_velocity(myDialog.slider1.value()))
myDialog.statusText.setText("Vehicle Velocity")

myDialog.show()

LogicThread.start()
app.exec()

# If GUI is closed tell thread to close
myLogicThread.killLoop = True
