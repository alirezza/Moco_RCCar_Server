import os
import sys
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QApplication,
    QDialog,
    QTabWidget,
    QLineEdit,
    QDialogButtonBox,
    QFrame,
    QListWidget,
    QGroupBox, QPushButton,
)
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QLabel, QFileDialog, QSlider, QWidget, \
    QGroupBox, QTabWidget, QDialogButtonBox
from PySide6.QtCore import *
import threading
import time

from PySide6.examples.widgets.dialogs.tabdialog.tabdialog import TabDialog

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

    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.continue_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.parking_button_clicked = True
        myLogicThread.myStateMachine.currentState.car_park()


@Slot()
def continue_car():

    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.trajectory.parking_button_clicked = False
        myLogicThread.myStateMachine.currentState.trajectory.continue_button_clicked = True
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
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        main_group = QGroupBox("Main")
        self.button6 = QPushButton("Start Car")
        self.button6.resize(250,50)
        self.button7 = QPushButton("Stop Car")
        self.button8 = QPushButton("Park")
        self.button9 = QPushButton("Continue")
        information_gruop = QGroupBox("Information")
        self.statusText_velo = QLabel("Speed: ")
        self.statusText_angle = QLabel("Steering angle: ")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.button6)
        main_layout.addWidget(self.button7)
        main_layout.addWidget(self.button8)
        main_layout.addWidget(self.button9)
        main_group.setLayout(main_layout)

        information_layout = QVBoxLayout()
        information_layout.addWidget(self.statusText_velo)
        information_layout.addWidget(self.statusText_angle)
        information_gruop.setLayout(information_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_group)
        main_layout.addWidget(information_gruop)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

        self.button6.clicked.connect(start_car)
        self.button7.clicked.connect(stop_car)
        self.button8.clicked.connect(park_car)
        self.button9.clicked.connect(continue_car)


class PathTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        path_group = QGroupBox("Path")

        self.button2 = QPushButton("Lock In Path")
        self.button3 = QPushButton("Clear Path")
        self.button4 = QPushButton("Load Path")
        self.button5 = QPushButton("Save Path")
        self.button11 = QPushButton("Create new Path")

        path_layout = QVBoxLayout()
        path_layout.addWidget(self.button2)
        path_layout.addWidget(self.button3)
        path_layout.addWidget(self.button5)
        path_layout.addWidget(self.button4)
        path_group.setLayout(path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(path_group)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.button2.clicked.connect(create_path)
        self.button3.clicked.connect(clear_path)
        self.button4.clicked.connect(lambda: load_path(self))
        self.button5.clicked.connect(lambda: save_path(self))
        self.button11.clicked.connect(newPath)

class SettingTab(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        setting_group = QGroupBox("Setting")

        self.button1 = QPushButton("Reset State Machine")
        self.button12 = QPushButton("Change Direction")
        self.button10 = QPushButton("Reset Corners")

        setting_layout = QVBoxLayout()
        setting_layout.addWidget(self.button1)
        setting_layout.addWidget(self.button12)
        setting_layout.addWidget(self.button10)
        setting_group.setLayout(setting_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(setting_group)
        main_layout.addStretch(1)
        self.setLayout(main_layout)
        self.button10.clicked.connect(resetCorner)
        self.button12.clicked.connect(changeDir)
        self.button1.clicked.connect(restart_state_machine)

# Create the Qt Application
app = QApplication([])

# Create Thread that runs in parallel to the gui
myLogicThread = LogicLoop()
LogicThread = threading.Thread(target=myLogicThread.loop, args=())

myDialog = TabDialog()

#myDialog.slider1.valueChanged.connect(lambda: set_velocity(myDialog.slider1.value()))
myDialog.show()

LogicThread.start()
app.exec()

# If GUI is closed tell thread to close
myLogicThread.killLoop = True
