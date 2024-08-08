from .helper import LineMovement, CircleCollider, ValueModifier
from .events import ConditionalEvent
import math

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.pattern = None
        self.collider = None

    def initialize(self, speed = 4, direction = 90, radius = 8):
        self.pattern = LineMovement(speed, direction)
        self.collider = CircleCollider(self.x, self.y, self.radius)
        self.radius = radius

    def clone(self):
        b = Bullet(self.x, self.y)
        b.pattern = self.pattern
        b.collider = self.collider
        b.radius = self.radius
        return b

    def getCollider(self):
        return self.collider

    def update(self, world):
        result = self.pattern.getNextValues(self.x, self.y, self.radius)
        self.x = result["x"]
        self.y = result["y"]
        self.radius = result["radius"]

        self.collider.position.x = self.x
        self.collider.position.y = self.y
        self.collider.radius = self.radius

        if not world.checkInWorld(self.x, self.y, self.radius):
            world.removeEntity(self)
        world.checkCollision(self)


class Spawner:
    def __init__(self, name):
        self.x = 0
        self.y = 0
        self.name = name
        self.movement = LineMovement(0, 0)

    def setStartingValues(self, x, y, speed = 0, direction = 0):
        self.x = x
        self.y = y
        self.movement.adjustParameters([speed, direction])

    def initialize(self, spawner):
        self.patternIndex = 0
        self.currentPatternTime = 0

        self.spawnPattern = []
        if ("pattern" in spawner):
            for p in spawner["pattern"]:
                self.spawnPattern.append(p.lower())
            
        if len(self.spawnPattern) == 0:
            self.spawnPattern.append("bullet")
        
        self.totalPatternTime = 0
        if "patternTime" in spawner:
            self.totalPatternTime = int(spawner["patternTime"])
        
        self.patternRepeat = 0
        if "patternRepeat" in spawner:
            self.patternRepeat = int(spawner["patternRepeat"])
        
        self.spawnerPhase = ValueModifier(0, 360, 0)
        if "spawnerPhase" in spawner:
            parts = spawner["spawnerPhase"].split(",")
            if len(parts) >= 1:
                self.spawnerPhase.minValue = float(parts[0])
            if len(parts) >= 2:
                self.spawnerPhase.maxValue = float(parts[1])
            if len(parts) >= 3:
                self.spawnerPhase.rate = float(parts[2])
            if len(parts) >= 4:
                self.spawnerPhase.timeBetween = float(parts[3])
            if len(parts) >= 5:
                self.spawnerPhase.type = parts[4].strip().lower()
        self.spawnerPhase.initialize()

        self.spawnerRadius = ValueModifier()
        if "spawnerRadius" in spawner:
            parts = spawner["spawnerRadius"].split(",")
            if len(parts) >= 1:
                self.spawnerRadius.minValue = float(parts[0])
            if len(parts) >= 2:
                self.spawnerRadius.maxValue = float(parts[1])
            if len(parts) >= 3:
                self.spawnerRadius.rate = float(parts[2])
            if len(parts) >= 4:
                self.spawnerRadius.timeBetween = float(parts[3])
            if len(parts) >= 5:
                self.spawnerRadius.type = parts[4].strip().lower()
        self.spawnerRadius.initialize()

        self.bulletRadius = ValueModifier(5)
        if "bulletRadius" in spawner:
            parts = spawner["bulletRadius"].split(",")
            if len(parts) >= 1:
                self.bulletRadius.minValue = float(parts[0])
            if len(parts) >= 2:
                self.bulletRadius.maxValue = float(parts[1])
            if len(parts) >= 3:
                self.bulletRadius.rate = float(parts[2])
            if len(parts) >= 4:
                self.bulletRadius.timeBetween = float(parts[3])
            if len(parts) >= 5:
                self.bulletRadius.type = parts[4].strip().lower()
        self.bulletRadius.initialize()

        self.spawnedSpeed = ValueModifier(2)
        if "spawnedSpeed" in spawner:
            parts = spawner["spawnedSpeed"].split(",")
            if len(parts) >= 1:
                self.spawnedSpeed.minValue = float(parts[0])
            if len(parts) >= 2:
                self.spawnedSpeed.maxValue = float(parts[1])
            if len(parts) >= 3:
                self.spawnedSpeed.rate = float(parts[2])
            if len(parts) >= 4:
                self.spawnedSpeed.timeBetween = float(parts[3])
            if len(parts) >= 5:
                self.spawnedSpeed.type = parts[4].strip().lower()
        self.spawnedSpeed.initialize()

        self.spawnedNumber = ValueModifier(1)
        if "spawnedNumber" in spawner:
            parts = spawner["spawnedNumber"].split(",")
            if len(parts) >= 1:
                self.spawnedNumber.minValue = float(parts[0])
            if len(parts) >= 2:
                self.spawnedNumber.maxValue = float(parts[1])
            if len(parts) >= 3:
                self.spawnedNumber.rate = float(parts[2])
            if len(parts) >= 4:
                self.spawnedNumber.timeBetween = float(parts[3])
            if len(parts) >= 5:
                self.spawnedNumber.type = parts[4].strip().lower()
        self.spawnedNumber.initialize()

        self.spawnedAngle = ValueModifier(360)
        self.spawnedAnglePlayer = False
        if "spawnedAngle" in spawner:
            if spawner["spawnedAngle"].strip().lower() == "player":
                self.spawnedAnglePlayer = True
            else:
                parts = spawner["spawnedAngle"].split(",")
                if len(parts) >= 1:
                    self.spawnedAngle.minValue = float(parts[0])
                if len(parts) >= 2:
                    self.spawnedAngle.maxValue = float(parts[1])
                if len(parts) >= 3:
                    self.spawnedAngle.rate = float(parts[2])
                if len(parts) >= 4:
                    self.spawnedAngle.timeBetween = float(parts[3])
                if len(parts) >= 5:
                    self.spawnedAngle.type = parts[4].strip().lower()
        self.spawnedAngle.initialize()

    def getCollider(self):
        return None

    def clone(self):
        spawner = Spawner(self.name)
        spawner.x = self.x
        spawner.y = self.y
        spawner.spawnPattern = self.spawnPattern
        spawner.patternIndex = self.patternIndex
        spawner.currentPatternTime = self.currentPatternTime
        spawner.totalPatternTime = self.totalPatternTime
        spawner.patternRepeat = self.patternRepeat
        spawner.spawnerPhase = self.spawnerPhase.clone()
        spawner.spawnerRadius = self.spawnerRadius.clone()
        spawner.bulletRadius = self.bulletRadius.clone()
        spawner.spawnedSpeed = self.spawnedSpeed.clone()
        spawner.spawnedNumber = self.spawnedNumber.clone()
        spawner.spawnedAngle = self.spawnedAngle.clone()
        spawner.spawnedAnglePlayer = self.spawnedAnglePlayer
        return spawner

    def update(self, world):
        if self.currentPatternTime > 0:
            self.currentPatternTime -= 1
        self.spawnerPhase.update()
        self.spawnerRadius.update()
        self.bulletRadius.update()
        self.spawnedNumber.update()
        self.spawnedSpeed.update()
        self.spawnedAngle.update()

        result = self.movement.getNextValues(self.x, self.y, 0)
        self.x = result["x"]
        self.y = result["y"]

        if not world.checkInWorld(self.x, self.y, self.spawnerRadius.currentValue):
            world.removeEntity(self)

        if self.currentPatternTime == 0:
            self.patternIndex = (self.patternIndex + 1) % len(self.spawnPattern)
            self.currentPatternTime = self.totalPatternTime

            if self.spawnPattern[self.patternIndex] != "wait":
                for i in range(0, math.floor(self.spawnedNumber.currentValue)):
                    positionX = self.x
                    positionY = self.y
                    if self.spawnedAnglePlayer:
                        spawnedAngle = math.atan2(world.player.y - self.y, world.player.x - self.x)
                    else:
                        spawnedAngle = self.movement.getParameters()[1] + self.spawnerPhase.currentValue + i * self.spawnedAngle.currentValue / math.floor(self.spawnedNumber.currentValue)
                        positionX += self.spawnerRadius.currentValue * math.cos(spawnedAngle * math.pi / 180)
                        positionY += self.spawnerRadius.currentValue * math.sin(spawnedAngle * math.pi / 180)
                    if self.spawnPattern[self.patternIndex] == "bullet":
                        bullet = Bullet(positionX, positionY)
                        bullet.initialize(self.spawnedSpeed.currentValue, spawnedAngle, self.bulletRadius.currentValue)
                        world.addEntity(bullet)
                    else:
                        spawner = world.definedSpawners[self.spawnPattern[self.patternIndex]].clone()
                        if spawner:
                            spawner.setStartingValues(positionX, positionY, self.spawnedSpeed.currentValue, spawnedAngle)
                            world.addEntity(spawner)
                if self.patternRepeat > 0:
                    self.patternRepeat -= 1
                    if self.patternRepeat == 0:
                        world.removeEntity(self)

class Player:
    def __init__(self, x, y, radius = 3, speed = 4, lives = 1):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.currentLives = lives
        self.invulnerable = False

    def initialize(self):
        self.originalX = self.x
        self.originalY = self.y
        self.collider = CircleCollider(self.x, self.y, self.radius)

    def getCollider(self):
        return self.collider

    def getLives(self):
        return self.currentLives

    def die(self, world):
        if self.invulnerable:
            return
        self.currentLives -= 1
        if self.currentLives > 0:
            world.removeAllBullets()
            self.x = self.originalX
            self.y = self.originalY

    def clone(self):
        p = Player(self.x, self.y, self.radius, self.speed, self.currentLives)
        p.originalX = self.originalX
        p.originalY = self.originalY
        p.collider = self.collider
        p.invulnerable = self.invulnerable
        return p

    def applyAction(self, action):
        if self.currentLives < 0:
            return
        delta = action.multiply(self.speed)
        self.x += delta.x
        self.y += delta.y

    def update(self, world):
        if self.x - self.radius < 0:
            self.x = self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.x + self.radius > world.width:
            self.x = world.width - self.radius
        if self.y + self.radius > world.height:
            self.y = world.height - self.radius
        self.collider.position.x = self.x
        self.collider.position.y = self.y
        self.collider.radius = self.radius

class GameScript:
    def __init__(self):
        self.currentIndex = 0
        self.events = []

    def initialize(self, script):
        self.currentIndex = 0
        self.events = []
        for s in script:
            self.events.append(ConditionalEvent(s))

    def clone(self):
        script = GameScript()
        script.events = self.events
        script.currentIndex = self.currentIndex
        return script

    def update(self, world, x, y, health):
        if self.currentIndex >= len(self.events):
            return
        if health <= self.events[self.currentIndex].health:
            self.events[self.currentIndex].apply(world, x, y)
            self.currentIndex += 1

class Boss:
    def __init__(self):
        self.script = GameScript()

    def initialize(self, width, height, script):
        self.x = width / 2
        self.y = height / 4
        self.maxHealth = 3000
        if "health" in script:
            self.maxHealth = int(script["health"])
        if "position" in script:
            parts = script["position"].split(",")
            if len(parts) >= 1:
                self.x = float(parts[0]) * width
            if len(parts) >= 2:
                self.y = float(parts[1]) * height
        if "script" in script:
            self.script.initialize(script["script"])
        self.health = self.maxHealth

    def clone(self):
        boss = Boss()
        boss.x = self.x
        boss.y = self.y
        boss.health = self.health
        boss.maxHealth = self.maxHealth
        boss.script = self.script.clone()
        return boss

    def getCollider(self):
        return None

    def getHealth(self):
        return self.health / self.maxHealth

    def update(self, world):
        self.health -= 1
        if self.health < 0:
            self.health = 0
        if not world.hideUnknown:
            self.script.update(world, self.x, self.y, 100 * self.health / self.maxHealth)

class World:
    def __init__(self, width, height, maximumBullets=0):
        self.width = width
        self.height = height
        self.maximumBullets = maximumBullets
        self.hideUnknown = False
        self.disableCollision = False
        self.bullets = []
        self.spawners = []
        self.created = []
        self.deleted = []
        self.bulletClass = Bullet

    def initialize(self, script):
        self.player = Player(self.width / 2, 0.8 * self.height)
        self.player.initialize()
        self.boss = Boss()
        if "spawners" in script:
            self.definedSpawners = {}
            for name in script["spawners"]:
                self.definedSpawners[name.lower()] = Spawner(name.lower())
                self.definedSpawners[name.lower()].initialize(script["spawners"][name])
        if "boss" in script:
            self.boss.initialize(self.width, self.height, script["boss"])

    def clone(self):
        newWorld = World(self.width, self.height, self.maximumBullets)
        for e in self.bullets:
            temp = e.clone()
            newWorld.bullets.append(temp)
        for e in self.spawners:
            temp = e.clone()
            newWorld.spawners.append(temp)
        newWorld.player = self.player.clone()
        newWorld.boss = self.boss.clone()
        newWorld.definedSpawners = self.definedSpawners
        newWorld.hideUnknown = self.hideUnknown
        newWorld.disableCollision = self.disableCollision
        return newWorld

    def isWon(self):
        if self.boss == None:
            return False
        return self.boss.getHealth() <= 0

    def checkInWorld(self, x, y, radius):
        return not(x + radius < 0 or y + radius < 0 or x - radius > self.width or y - radius > self.height)

    def isLose(self):
        if self.player == None:
            return False
        return self.player.getLives() <= 0

    def checkCollision(self, entity):
        if self.disableCollision:
            return 
        result = self.player.getCollider().checkCollision(entity.getCollider())
        if result:
            self.player.die(self)

    def addEntity(self, entity):
        self.created.append(entity)

    def removeEntity(self, entity):
        self.deleted.append(entity)

    def removeAllBullets(self):
        self.deleted = self.deleted.concat(self.bullets)

    def removeAllSpawners(self):
        self.deleted = self.deleted.concat(self.spawners)

    def removeSpawners(self, name):
        for s in self.spawners:
            if name.lower() == s.name.lower():
                self.deleted.append(s)

    def update(self, action):
        if self.isLose() or self.isWon():
            return

        if self.player != None and not self.disableCollision:
            self.player.applyAction(action)
            self.player.update(self)
        if self.boss != None:
            self.boss.update(self)
        for s in self.spawners:
            s.update(self)

        removeExtra=0
        if len(self.bullets) > self.maximumBullets and self.maximumBullets > 0:
            removeExtra = len(self.bullets) - self.maximumBullets
        tooManyBullets = removeExtra > 0
        
        for b in self.bullets:
            if removeExtra > 0:
                removeExtra -= 1
                self.removeEntity(b)
            else:
                b.update(self)

        for e in self.created:
            if isinstance(e, Bullet) and e not in self.bullets:
                self.bullets.append(e)
            if isinstance(e, Spawner) and e not in self.spawners:
                self.spawners.append(e)
        self.created = []
        for e in self.deleted:
            if isinstance(e, Bullet) and e in self.bullets:
                self.bullets.remove(e)
            if isinstance(e, Spawner) and e in self.spawners:
                self.spawners.remove(e)
        self.deleted = []

        return not tooManyBullets