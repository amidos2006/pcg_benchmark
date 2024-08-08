from .helper import ActionNumber, getSafestBucket, calculateBuckets
import math

class TreeNode:
    def __init__(self, parent, action, world, parameters):
        self.parent = parent
        self.children = [None, None, None, None, None]
        self.action = action
        self.world = world
        self.parameters = parameters
        tempWorld = world.clone()
        self.safezone = 0
        for _ in range(10):
            tempWorld.update(ActionNumber.getAction(ActionNumber.NONE))
            if tempWorld.isLose() or len(tempWorld.spawners) > parameters["maxNumSpawners"]:
                break
            if tempWorld.isWon():
                self.safezone = 10.0
                break
            self.safezone += 1.0
        self.safezone = self.safezone / 10.0
        self.numChildren = 0

    def addChild(self, action, parameters):
        newWorld = self.world.clone()
        for _ in range(parameters["repeatingAction"]):
            newWorld.update(ActionNumber.getAction(action))
            if newWorld.isLose() or len(newWorld.spawners) > parameters["maxNumSpawners"]:
                break
        self.children[action] = TreeNode(self, action, newWorld, self.parameters)
        self.numChildren += 1
        return self.children[action]

    def getEvaluation(self, target):
        isLose = 0
        if self.world.isLose():
            isLose = 1

        bucketWidth = self.parameters["width"] / self.parameters["bucketsX"]
        bucketHeight = self.parameters["height"] / self.parameters["bucketsY"]
        p = {
            "x": math.floor(self.world.player.x / bucketWidth),
            "y": math.floor(self.world.player.y / bucketHeight)
        }
        return 0.5 * (1 - self.world.boss.getHealth()) - isLose + 0.5 * self.safezone + \
            - 0.25 * (abs(p["x"] - target["x"]) + abs(p["y"] - target["y"]))

    def getSequence(self):
        result = []
        currentNode = self
        while currentNode.parent != None:
            result.append(currentNode.action)
            currentNode = currentNode.parent
        result.reverse()
        return result
    
class AStar:
    def __init__(self):
        self.oldActions = []

    def initialize(self):
        return

    def getAction(self, world, value, parameters): 
        if len(self.oldActions) > 0:
            action = self.oldActions.pop(0)
            return action
        tempWorld = world.clone()
        tempWorld.hideUnknown = True
        openNodes = [TreeNode(None, -1, tempWorld, parameters)]
        allNodes = []
        currentNumbers = 0
        solution = []
        buckets = calculateBuckets(parameters["width"], parameters["height"], parameters["bucketsX"], parameters["bucketsY"], world.bullets)
        bucketWidth = parameters["width"] / parameters["bucketsX"]
        bucketHeight = parameters["height"] / parameters["bucketsY"]
        target = getSafestBucket(math.floor(world.player.x / bucketWidth), 
            math.floor(world.player.y / bucketHeight), parameters["bucketsX"], buckets)
        while len(openNodes) > 0:
            openNodes.sort(key=lambda a: a.getEvaluation(target))
            currentNode = openNodes.pop()
            allNodes.append(currentNode)
            if len(currentNode.world.spawners) > parameters["maxNumSpawners"]:
                return -1
            if currentNode.world.isWon():
                solution = node.getSequence()
                break
            if currentNumbers >= value or currentNode.world.isLose():
                continue
            for i in range(len(currentNode.children)):
                node = currentNode.addChild(i, parameters)
                if len(node.world.spawners) > parameters["maxNumSpawners"]:
                    return -1
                if node.world.isWon():
                    solution = node.getSequence()
                    break
                openNodes.append(node)
                currentNumbers += 1
        if len(solution) > 0:
            self.oldActions = [solution[0]] * parameters["repeatingAction"]
            action = self.oldActions.pop(0)
            return action
        bestNode = None
        for n in allNodes:
            if n.numChildren == 0:
                if bestNode == None:
                    bestNode = n
                elif bestNode.getEvaluation(target) < n.getEvaluation(target):
                    bestNode = n
        if bestNode == None:
            return -1
        self.oldActions = [bestNode.getSequence()[0]] * parameters["repeatingAction"]
        action = self.oldActions.pop(0)
        return action