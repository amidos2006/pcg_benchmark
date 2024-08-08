from ..core import MarioAgent
from ..helper import MarioActions

class Agent(MarioAgent):
    def initialize(self, model):
        self._actions = [False] * MarioActions.numberOfActions()
        self._actions[MarioActions.RIGHT.value] = True
        self._actions[MarioActions.SPEED.value] = True

    def getActions(self, model):
        self._actions[MarioActions.SPEED.value] = model.mayMarioJump() or not model.isMarioOnGround()
        self._actions[MarioActions.JUMP.value] = model.mayMarioJump() or not model.isMarioOnGround()
        return self._actions

    def getAgentName(self):
        return "SergeyKarakovskiyAgent"