import sys
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import Slot
import threading
import time


class State:
    def run(self):
        assert 0, "run not implemented"

    def next(self):
        assert 0, "next not implemented"


class StateMachine:
    def __init__(self, initState):
        self.currentState = initState

    def run(self):
        self.currentState.run()
        self.currentState = self.currentState.next()

    def setNextState(self, nextState):
        self.currentState = nextState


class State1(State):
    def __init__(self):
        self.i = 0

    def run(self):
        self.i += 1
        print(self.i)

    def next(self):
        if(self.i<3):
            return self
        else:
            return State2()


class State2(State):

    def run(self):
        print("State 2 Active")
        return

    def next(self):
        return self

class LogicLoop:
    killLoop = False

    def __init__(self):
        self.myStateMachine = StateMachine(State1())
        self.killLoop = False

    def loop(self):
        while self.killLoop == False:
            self.myStateMachine.run()
            time.sleep(1)  # Nur zu Demo Zwecken warten, eine open CV Loop würde hier natürlich nicht beschränkt werden
        print("Logic Loop Ended")


@Slot()
def restart_state_machine():
    myLogicThread.myStateMachine = StateMachine(State1())
    print("Restart")


# Create the Qt Application
app = QApplication([])

# Create Thread that runs in parallel to the gui
myLogicThread = LogicLoop()
LogicThread = threading.Thread(target=myLogicThread.loop, args=())

# Create a button, connect it and show it
button = QPushButton("Restart State Machine")
button.clicked.connect(restart_state_machine)
button.show()

LogicThread.start()
app.exec()

# If GUI is closed tell thread to close
myLogicThread.killLoop = True


