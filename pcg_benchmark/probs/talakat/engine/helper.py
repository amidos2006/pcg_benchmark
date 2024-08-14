from enum import Enum
import math

def calculateEntropy(values):
    entropy = 0
    for p in values:
        if p > 0 and p < 1:
            entropy += p * math.log(p) / math.log(len(values))
    return -entropy

def calculateBuckets(width, height, bucketsX, bucketsY, bullets):
    bucketWidth = width / bucketsX
    bucketHeight = height / bucketsY

    buckets = []
    for _ in range(bucketsX * bucketsY):
        buckets.append(0)

    s = Point()
    e = Point()
    for b in bullets:
        indeces = []
        s.x = math.ceil(round(4 * (b.x - b.radius) / bucketWidth)/4)
        s.y = math.ceil(round(4 * (b.y - b.radius) / bucketHeight)/4)
        if s.x < 0:
            s.x = 0
        if s.y < 0:
            s.y = 0
        if s.x >= bucketsX:
            s.x = bucketsX - 1
        if s.y >= bucketsY:
            s.y = bucketsY - 1
        e.x = math.floor(round(4 * (b.x + b.radius) / bucketWidth)/4)
        e.y = math.floor(round(4 * (b.y + b.radius) / bucketHeight)/4)
        if e.x < 0:
            e.x = 0
        if e.y < 0:
            e.y = 0
        if e.x >= bucketsX:
            e.x = bucketsX - 1
        if e.y >= bucketsY:
            e.y = bucketsY - 1
        for x in range(s.x, e.x + 1):
            for y in range(s.y, e.y + 1):
                index = y * bucketsX + x
                if index not in indeces:
                    indeces.append(index)
        for index in indeces:
            if index < 0 or index >= len(buckets):
                continue
            buckets[index] += 1
    return buckets

def _calculateSurroundingBullets(x, y, bucketX, riskDistance, buckets):
    result = 0
    for index in range(len(buckets)):
        bx = index % bucketX
        by = math.floor(index / bucketX)
        dist = abs(bx - x) + abs(by - y)
        if dist <= riskDistance:
            result += buckets[index] / (dist + 1)
    return result

def getSafestBucket(px, py, bucketX, buckets):
    bestX = px
    bestY = py
    for i in range(len(buckets)):
        x = i % bucketX
        y = math.floor(i / bucketX)
        if _calculateSurroundingBullets(x, y, bucketX, 4, buckets) <\
            _calculateSurroundingBullets(bestX, bestY, bucketX, 4, buckets):
            bestX = x
            bestY = y
    return {"x": bestX, "y":bestY}

class ActionNumber(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    NONE = 4
    LEFT_UP = 5
    RIGHT_UP = 6
    LEFT_DOWN = 7
    RIGHT_DOWN = 8

    def getAction(action):
        if action == ActionNumber.LEFT:
            return Point(-1, 0)
        if action == ActionNumber.RIGHT:
            return Point(1, 0)
        if action == ActionNumber.UP:
            return Point(0, -1)
        if action == ActionNumber.DOWN:
            return Point(0, 1)
        if action == ActionNumber.LEFT_DOWN:
            return Point(-1, 1)
        if action == ActionNumber.RIGHT_DOWN:
            return Point(1, 1)
        if action == ActionNumber.LEFT_UP:
            return Point(-1, -1)
        if action == ActionNumber.RIGHT_UP:
            return Point(1, -1)
        return Point()

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def add(self, x=0, y=0):
        return Point(self.x + x, self.y + y)

    def subtract(self, x=0, y=0):
        return Point(self.x - x, self.y - y)

    def multiply(self, value=1):
        return Point(self.x * value, self.y * value)

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Point(self.x/mag, self.y/mag)
        return Point(self.x, self.y)

    def magnitude(self):
        return math.sqrt(pow(self.x, 2) + pow(self.y, 2))
    
class ValueModifier:
    def __init__(self, minValue = 0, maxValue = 0, rate = 0, timeBetween = 0, type = "none"):
        self.minValue = minValue
        self.maxValue = maxValue
        if self.minValue > self.maxValue and rate != 0:
            self.minValue = maxValue
            self.maxValue = minValue
        self.rate = rate
        self.timeBetween = timeBetween
        self.type = type

    def initialize(self):
        self.currentValue = self.minValue
        self.currentRate = self.rate
        self.currentTimer = 0

    def clone(self):
        temp = ValueModifier()
        temp.minValue = self.minValue
        temp.maxValue = self.maxValue
        temp.rate = self.rate
        temp.timeBetween = self.timeBetween
        temp.type = self.type
        temp.currentValue = self.currentValue
        temp.currentRate = self.currentRate
        temp.currentTimer = self.currentTimer
        return temp

    def update(self): 
        if self.currentRate == 0:
            return
        
        self.currentTimer -= 1
        if self.currentTimer <= 0:
            self.currentValue += self.currentRate
            self.currentTimer = self.timeBetween
        
        if self.currentValue > self.maxValue:
            if self.type == "reverse":
                self.currentValue = self.maxValue
                self.currentRate *= -1
            elif self.type == "circle":
                self.currentValue = self.currentValue - self.maxValue + self.minValue
            else:
                self.currentValue = self.maxValue
        
        if self.currentValue < self.minValue:
            if self.type == "reverse":
                self.currentValue = self.minValue
                self.currentRate *= -1
            elif self.type == "circle":
                self.currentValue = self.currentValue + self.maxValue - self.minValue
            else:
                self.currentValue = self.minValue

class LineMovement:
    def __init__(self, speed, direction):
        self.speed = Point(speed * math.cos(direction * math.pi / 180),
                speed * math.sin(direction * math.pi / 180))
        self.speedMag = speed
        self.direction = direction

    def adjustParameters(self, newValues):
        self.speed = Point(newValues[0] * math.cos(newValues[1] * math.pi / 180),
                newValues[0] * math.sin(newValues[1] * math.pi / 180))
        self.speedMag = newValues[0]
        self.direction = newValues[1]

    def getParameters(self):
        return [self.speedMag, self.direction]

    def getNextValues(self, x, y, radius):
        return {
            "x": x + self.speed.x,
            "y": y + self.speed.y,
            "radius": radius
        }
        

class CircleCollider:
    def __init__(self, x, y, radius):
        self.position = Point(x, y)
        self.radius = radius

    def checkCollision(self, c):
        if isinstance(c,CircleCollider):
            distance = c.position.subtract(self.position.x, self.position.y).magnitude()
            colDist = c.radius + self.radius
            return distance < colDist
        return False