import threading

from PySide6.QtCore import *
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QLabel, QSlider, QLineEdit

from Configuration import ServerConfig
from StateLib import *
from State_ControlCar import StateControlCar


class LogicLoop:
    killLoop = False

    def __init__(self):
        self.myStateMachine = StateMachine(StateControlCar())
        self.killLoop = False

    def loop(self):
        while not self.killLoop:
            self.myStateMachine.run()

        self.myStateMachine.currentState.on_leave()
        print("Logic Loop Ended")


@Slot()
def restart_state_machine():
    myLogicThread.myStateMachine.force_next_state(StateControlCar())
    print("Restart")


@Slot()
def start_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.start_car()


@Slot()
def stop_car():
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.stop_car()


@Slot()
def set_velocity(vel):
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        #myLogicThread.myStateMachine.currentState.set_velocity(myDialog.inputfield.text())
        #myDialog.statusText3.setText((str(myDialog.inputfield.text())))
        myLogicThread.myStateMachine.currentState.set_velocity(vel)
        myDialog.statusText3.setText(str(vel))
    print("velocity: " + myDialog.inputfield.text())


@Slot()
def set_angle(vel):
    if isinstance(myLogicThread.myStateMachine.currentState, StateControlCar):
        myLogicThread.myStateMachine.currentState.set_angle(vel)
    print("angle: " + str(vel))


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # Create widgets
        self.button1 = QPushButton("Reset State Machine")
        self.button6 = QPushButton("Start Car")
        self.button7 = QPushButton("Stop Car")
        self.slider1 = QSlider(Qt.Horizontal)
        self.statusText1 = QLabel("Status Label")
        self.slider2 = QSlider(Qt.Horizontal)
        self.statusText2 = QLabel("Status Label")
        self.statusText3 = QLabel("Status Label")
        self.inputfield = QLineEdit()

        self.slider2.setRange(-30, 30)
        self.slider2.setTickInterval(1)
        self.slider2.setValue(ServerConfig.getInstance().testingsteeringangle)

        self.slider1.setRange(0, 170)
        self.slider1.setTickInterval(5)
        self.slider1.setValue(ServerConfig.getInstance().vehicle_const_speed)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button6)
        layout.addWidget(self.button7)
        layout.addWidget(self.statusText1)
        layout.addWidget(self.statusText3)
        #layout.addWidget(self.inputfield)
        layout.addWidget(self.slider1)
        layout.addWidget(self.statusText2)
        layout.addWidget(self.slider2)

        # Set dialog layout
        self.setLayout(layout)


# Create the Qt Application
app = QApplication([])

# Create Thread that runs in parallel to the gui
myLogicThread = LogicLoop()
LogicThread = threading.Thread(target=myLogicThread.loop, args=())

myDialog = Form()
myDialog.button1.clicked.connect(restart_state_machine)
myDialog.button6.clicked.connect(start_car)
myDialog.button7.clicked.connect(stop_car)
myDialog.slider1.valueChanged.connect(lambda: set_velocity(myDialog.slider1.value()))
myDialog.statusText1.setText("Vehicle Velocity")
myDialog.slider2.valueChanged.connect(lambda: set_angle(myDialog.slider2.value()))
myDialog.statusText2.setText("Vehicle Angle")
myDialog.statusText3.setText(str(ServerConfig.getInstance().vehicle_const_speed))

myDialog.show()

LogicThread.start()
app.exec()

# If GUI is closed tell thread to close
myLogicThread.killLoop = True
