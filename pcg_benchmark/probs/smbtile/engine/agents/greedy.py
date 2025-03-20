from ..core import MarioAgent
from ..helper import MarioActions, GameStatus

def createAction(left, right, down, jump, speed):
    action = [False] * MarioActions.numberOfActions()
    action[MarioActions.DOWN.value] = down
    action[MarioActions.JUMP.value] = jump
    action[MarioActions.LEFT.value] = left
    action[MarioActions.RIGHT.value] = right
    action[MarioActions.SPEED.value] = speed
    return action

def canJumpHigher(model):
    return model.mayMarioJump() or model.getMarioCanJumpHigher()

def createPossibleActions(model):
    possibleActions = []
    # jump
    if canJumpHigher(model):
        possibleActions.append(createAction(False, False, False, True, False))
    if canJumpHigher(model):
        possibleActions.append(createAction(False, False, False, True, True))

    # run right
    possibleActions.append(createAction(False, True, False, False, True))
    if canJumpHigher(model):
        possibleActions.append(createAction(False, True, False, True, True))
    possibleActions.append(createAction(False, True, False, False, False))
    if canJumpHigher(model):
        possibleActions.append(createAction(False, True, False, True, False))

    return possibleActions

def getMarioDamage(model, prevModel):
    damage = 0
    if prevModel.getMarioMode() > model.getMarioMode():
        damage += 1
    if model.getGameStatus() == GameStatus.LOSE:
        if model.getMarioFloatPos()[1] > model.getLevelFloatDimensions()[1] - 20:
            damage += 5
        else:
            damage += 2
    return damage

def heuristic(model, prevModel):
    distance = model.getMarioFloatPos()[0] + 10 * model.getMarioFloatVelocity()[0] - prevModel.getMarioFloatPos()[0]
    return distance - getMarioDamage(model, prevModel) * 1000000

class Agent(MarioAgent):
    def initialize(self, model):
        self._maxRepeatLength = MarioAgent.stickyActions
        self._repeatLength = self._maxRepeatLength
        self._action = None
        return

    def getActions(self, model):
        if self._action == None or self._repeatLength == 0:
            possibleActions = createPossibleActions(model)
            bestAction = [False] * MarioActions.numberOfActions()
            bestHeuristic = -1000000000
            for action in possibleActions:
                newModel = model.clone()
                for _ in range(self._repeatLength):
                    newModel.advance(action)
                if heuristic(newModel, model) > bestHeuristic:
                    bestAction = action
                    bestHeuristic = heuristic(newModel, model)
            self._action = bestAction
            self._repeatLength = self._maxRepeatLength
        self._repeatLength -= 1
        return self._action

    def getAgentName(self):
        return "GreedyAgent"