from ..core import MarioAgent
from ..helper import MarioActions, GameStatus

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

def getActionString(action):
    s = ""
    if action[MarioActions.RIGHT.value]:
        s += "Forward "
    if action[MarioActions.LEFT.value]:
        s += "Backward "
    if action[MarioActions.SPEED.value]:
        s += "Speed "
    if action[MarioActions.JUMP.value]:
        s += "Jump "
    if action[MarioActions.DOWN.value]:
        s += "Duck"
    if len(s) == 0:
        s = "[NONE]"
    return s

def createAction(left, right, down, jump, speed):
    action = [False] * MarioActions.numberOfActions()
    action[MarioActions.DOWN.value] = down
    action[MarioActions.JUMP.value] = jump
    action[MarioActions.LEFT.value] = left
    action[MarioActions.RIGHT.value] = right
    action[MarioActions.SPEED.value] = speed
    return action

def canJumpHigher(node):
    return node._model.mayMarioJump() or node._model.getMarioCanJumpHigher()

def sameAction(action1, action2):
    for i in range(len(action1)):
        if action1[i] != action2[i]:
            return False
    return True

def createPossibleActions(node):
    possibleActions = []
    # jump
    if canJumpHigher(node):
        possibleActions.append(createAction(False, False, False, True, False))
    if canJumpHigher(node):
        possibleActions.append(createAction(False, False, False, True, True))

    # run right
    possibleActions.append(createAction(False, True, False, False, True))
    if canJumpHigher(node):
        possibleActions.append(createAction(False, True, False, True, True))
    possibleActions.append(createAction(False, True, False, False, False))
    if canJumpHigher(node):
        possibleActions.append(createAction(False, True, False, True, False))

    # run left
    possibleActions.append(createAction(True, False, False, False, False))
    if canJumpHigher(node):
        possibleActions.append(createAction(True, False, False, True, False))
    possibleActions.append(createAction(True, False, False, False, True))
    if canJumpHigher(node):
        possibleActions.append(createAction(True, False, False, True, True))

    return possibleActions

class TreeNode:
    def __init__(self, action, repetitions, model, parent):
        self._model = model.clone()
        self._repetitions = repetitions
        if action != None:
            self._action = action
            for _ in range(repetitions):
                self._model.advance(action)
        else:
            self._action = [False] * MarioActions.numberOfActions()
        self._parent = parent
        self._depth = 0
        self._root = self
        self._children = []
        if self._parent != None:
            self._depth += self._parent._depth + 1
            self._root = self._parent._root

    def onFloor(self):
        return self._model.isMarioOnGround()

    def getHeuristic(self):
        distance = 0
        if self._root != None:
            distance = self._model.getMarioFloatPos()[0] + 10 * self._model.getMarioFloatVelocity()[0] - self._root._model.getMarioFloatPos()[0]
        return distance - getMarioDamage(self._model, self._parent._model) * 1000000
    
    def getCost(self):
        return self._depth * self._repetitions

    def generateChildren(self):
        self._children = []
        possibleActions = createPossibleActions(self)
        if self.isLeafNode():
            possibleActions.clear()
        for action in possibleActions:
            self._children.append(TreeNode(action, self._repetitions, self._model, self))
        return self._children
    
    def getNextActions(self):
        result = []
        current = self
        while current != current._root:
            for _ in range(self._repetitions):
                result.append(current._action)
            current = current._parent
        result.reverse()
        return result
    
    def isLeafNode(self):
        return self._model.getGameStatus() != GameStatus.RUNNING
    
    def getKey(self):
        return [int(self._model.getMarioFloatPos()[0]), int(self._model.getMarioFloatPos()[1]), self._depth * self._repetitions]

    
class AStarTree:
    def __init__(self, reptitions):
        self._repetitions = reptitions
    
    def search(self, model, maxIterations):
        root = TreeNode(None, self._repetitions, model, None)
        visitedStates = []
        queue = root.generateChildren()
        bestNode = root
        bestTotal = -10000000000000 

        while len(queue) > 0 and maxIterations > 0:
            queue = sorted(queue, key=lambda v: v.getHeuristic() - 0.9 * v.getCost(), reverse=True)
            current = queue.pop(0)
            if self.isInVisited(visitedStates, current.getKey()):
                continue
            visitedStates.append(current.getKey())
            if current._model.getGameStatus() == GameStatus.WIN:
                return current.getNextActions()
            if current.getHeuristic() - 0.9 * current.getCost() > bestTotal and (current.onFloor() or bestNode == root):
                bestTotal = current.getHeuristic() - 0.9 * current.getCost()
                bestNode = current
            queue = queue + current.generateChildren()
            maxIterations -= 1
        return bestNode.getNextActions()
    
    def isInVisited(self, visitedStates, key):
        timeDiff = 5
        xDiff = 2
        yDiff = 2
        for v in visitedStates:
            if abs(v[0] - key[0]) < xDiff and abs(v[1] - key[1]) < yDiff and abs(v[2] - key[2]) < timeDiff and key[2] >= v[2]:
                return True
        return False

class Agent(MarioAgent):
    def initialize(self, model):
        self._maxIterations = MarioAgent.iterations
        self._maxRepetitions = MarioAgent.stickyActions
        self._repetitions = self._maxRepetitions
        self._action = None
        self.tree = AStarTree(self._maxRepetitions)

    def getActions(self, model):
        if self._action == None or len(self._action) == 0:
            self._action = self.tree.search(model, self._maxIterations)
        return self._action.pop(0)

    def getAgentName(self):
        return "DeterminsticAStarAgent"