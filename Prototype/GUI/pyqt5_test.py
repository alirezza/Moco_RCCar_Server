import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton


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


class DummyState(State):
    count = 0

    def run(self):
        if self.count < 5:
            self.count += 1
            print(self.count)

    def next(self):
        if self.count < 5:
            return self
        else:
            return DummyState2()


class DummyState2(State):
    flag = True

    def run(self):
        if self.flag:
            print('finished')
            self.flag = False

    def next(self):
        return self


class DummyWidget(QtWidgets):

    def paintEvent(self, a):
        print('Hallo')
        super().paintEvent(a)


@pyqtSlot()
def button_logic():
    print('button pressed')

def main():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(200, 200, 300, 300)
    win.setWindowTitle("My first window!")

    label = QLabel(win)
    label.setText("my first label")
    label.move(50, 50)

    button = QPushButton('click me', win)
    button.clicked.connect(button_logic)
    button.move(100, 100)

    widget = DummyWidget(win)

    win.show()
    sys.exit(app.exec_())


myStateMachine = StateMachine(DummyState())

main()  # make sure to call the function
while True:
    myStateMachine.run()
