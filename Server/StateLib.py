class State:
    def run(self):
        assert 0, "run not implemented"

    def next(self):
        assert 0, "next not implemented"

    def on_enter(self):
        assert 0, "next not implemented"

    def on_leave(self):
        assert 0, "next not implemented"


class StateMachine:

    def __init__(self, init_state):
        self.currentState = init_state
        self.currentState.on_enter()
        self.forceFlag = False
        self.forceState = 0

    def run(self):
        self.currentState.run()

        next_state = self.currentState.next()

        if self.forceFlag:
            self.forceFlag = False
            self.set_next_state(self.forceState)
        elif self.currentState != next_state:
            self.set_next_state(next_state)


    def set_next_state(self, next_state):
        if self.currentState != next_state:
            self.currentState.on_leave()
            self.currentState = next_state
            self.currentState.on_enter()

    def force_next_state(self, next_state):
        self.forceFlag = True
        self.forceState = next_state



