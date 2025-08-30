from .helper import SpriteType, EventType, MarioActions, GameStatus, TileFeature
from .sprites import Mario, Enemy, BulletBill, FlowerEnemy, Mushroom, FireFlower, LifeMushroom, spawnSprite
import time
import numpy as np

class MarioAgent:
    def __init__(self, seed = None):
        if seed == None:
            self._random = np.random.default_rng()
        else:
            self._random = np.random.default_rng(seed)
    
    def initialize(self, model):
        raise NotImplementedError("implement the initialize function")
    
    def getActions(self, model):
        raise NotImplementedError("implementat the getActions function")
    
    def getAgentName(self):
        raise NotImplementedError("implement the getAgentName function")
    
class MarioAgentEvent:
    def __init__(self, actions, marioX, marioY, marioState, marioOnGround, time):
        self._actions = actions
        self._marioX = marioX
        self._marioY = marioY
        self._marioState = marioState
        self._marioOnGround = marioOnGround
        self._time = time

    def getActions(self):
        return self._actions

    def getMarioX(self):
        return self._marioX

    def getMarioY(self):
        return self._marioY

    def getMarioState(self):
        return self._marioState

    def getMarioOnGround(self):
        return self._marioOnGround

    def getTime(self):
        return self._time
    
class MarioEvent:
    def __init__(self, eventType, eventParam = 0, x = 0, y = 0, state = 0, time = 0):
        self._eventType = eventType
        self._eventParam = eventParam
        self._marioX = x
        self._marioY = y
        self._marioState = state
        self._time = time

    def getEventType(self):
        return self._eventType.value

    def getEventParam(self):
        return self._eventParam

    def getMarioX(self):
        return self._marioX

    def getMarioY(self):
        return self._marioY

    def getMarioState(self):
        return self._marioState

    def getTime(self):
        return self._time

    def __eq__(self, other):
        return self._eventType.value == other._eventType.value and\
                (self._eventParam == 0 or self._eventParam == other._eventParam)

    def __ne__(self, other):
        return not self.__eq__(other)
    
class MarioGame:
    maxMoves = 100
    graceTime = 10
    width = 256
    height = 256
    tileWidth = width / 16
    tileHeight = height / 16
    verbose = False

    def __init__(self, killEvents = []):
        self.pause = False

        self._killEvents = killEvents
        self._agent = None
        self._world = None

    def getDelay(self, fps):
        if fps <= 0:
            return 0
        return 1000 / fps

    def setAgent(self, agent):
        self._agent = agent

    def runGame(self, agent, level, timer, marioState = 0):
        self.setAgent(agent)
        return self._gameLoop(level, timer, marioState)

    def _gameLoop(self, level, timer, marioState):
        self._world = MarioWorld(self._killEvents)
        self._world.initializeLevel(level, 1000 * timer)
        self._world.mario.isLarge = marioState > 0
        self._world.mario.isFire = marioState > 1
        self._world.update([0]*MarioActions.numberOfActions())

        MarioForwardModel.maxMoves = MarioGame.maxMoves
        fwdModel = MarioForwardModel(self._world.clone())
        self._agent.initialize(fwdModel)

        gameEvents = []
        agentEvents = []
        while self._world.gameStatus == GameStatus.RUNNING:
            if not self.pause: 
                # get actions
                MarioForwardModel.maxMoves = MarioGame.maxMoves
                actions = self._agent.getActions(MarioForwardModel(self._world.clone()))
                if MarioGame.verbose:
                    if MarioForwardModel.maxMoves < 0 and abs(MarioForwardModel.maxMoves) > MarioGame.graceTime:
                        print("The Agent is slowing down the game by: " + abs(MarioForwardModel.maxMoves) + " moves.")
                # update world
                self._world.update(actions)
                gameEvents += self._world.lastFrameEvents
                agentEvents.append(MarioAgentEvent(actions, self._world.mario.x,
                        self._world.mario.y, int(self._world.mario.isLarge) + int(self._world.mario.isFire),
                        self._world.mario.onGround, self._world.currentTick))
        return MarioResult(self._world, gameEvents, agentEvents)
    
class MarioForwardModel: 
    OBS_SCENE_SHIFT = 16

    # Generic values
    OBS_NONE = 0
    OBS_UNDEF = -42

    # Common between scene detail level 0 and scene detail level 1
    OBS_SOLID = OBS_SCENE_SHIFT + 1
    OBS_BRICK = OBS_SCENE_SHIFT + 6
    OBS_QUESTION_BLOCK = OBS_SCENE_SHIFT + 8
    OBS_COIN = OBS_SCENE_SHIFT + 15
    # Scene detail level 0
    OBS_PYRAMID_SOLID = OBS_SCENE_SHIFT + 2
    OBS_PIPE_BODY_RIGHT = OBS_SCENE_SHIFT + 21
    OBS_PIPE_BODY_LEFT = OBS_SCENE_SHIFT + 20
    OBS_PIPE_TOP_RIGHT = OBS_SCENE_SHIFT + 19
    OBS_PIPE_TOP_LEFT = OBS_SCENE_SHIFT + 18
    OBS_USED_BLOCK = OBS_SCENE_SHIFT + 14
    OBS_BULLET_BILL_BODY = OBS_SCENE_SHIFT + 5
    OBS_BULLET_BILL_NECT = OBS_SCENE_SHIFT + 4
    OBS_BULLET_BILL_HEAD = OBS_SCENE_SHIFT + 3
    OBS_BACKGROUND = OBS_SCENE_SHIFT + 47
    OBS_PLATFORM_SINGLE = OBS_SCENE_SHIFT + 43
    OBS_PLATFORM_LEFT = OBS_SCENE_SHIFT + 44
    OBS_PLATFORM_RIGHT = OBS_SCENE_SHIFT + 45
    OBS_PLATFORM_CENTER = OBS_SCENE_SHIFT + 46
    # Scene detail level 1
    OBS_PLATFORM = OBS_SCENE_SHIFT + 43
    OBS_CANNON = OBS_SCENE_SHIFT + 3
    OBS_PIPE = OBS_SCENE_SHIFT + 18
    # Scene detail level 2
    OBS_SCENE_OBJECT = OBS_SCENE_SHIFT + 84

    # Common between enemies detail level 0 and 1
    OBS_FIREBALL = 16
    # Enemies Detail 0
    OBS_GOOMBA = 2
    OBS_GOOMBA_WINGED = 3
    OBS_RED_KOOPA = 4
    OBS_RED_KOOPA_WINGED = 5
    OBS_GREEN_KOOPA = 6
    OBS_GREEN_KOOPA_WINGED = 7
    OBS_SPIKY = 8
    OBS_SPIKY_WINGED = 9
    OBS_BULLET_BILL = 10
    OBS_ENEMY_FLOWER = 11
    OBS_MUSHROOM = 12
    OBS_FIRE_FLOWER = 13
    OBS_SHELL = 14
    OBS_LIFE_MUSHROOM = 15
    # Enemies Detail 1
    OBS_STOMPABLE_ENEMY = 2
    OBS_NONSTOMPABLE_ENEMY = 8
    OBS_SPECIAL_ITEM = 12
    # Enemies Detail 2
    OBS_ENEMY = 1

    def getSpriteTypeGeneralization(sprite, detail):
        if detail == 0:
            if sprite == SpriteType.MARIO:
                return MarioForwardModel.OBS_NONE
            return sprite
        if detail == 1:
            if sprite == SpriteType.MARIO:
                return MarioForwardModel.OBS_NONE
            if sprite == SpriteType.FIREBALL:
                return MarioForwardModel.OBS_FIREBALL
            if sprite == SpriteType.MUSHROOM or sprite == SpriteType.LIFE_MUSHROOM or sprite == SpriteType.FIRE_FLOWER:
                return MarioForwardModel.OBS_SPECIAL_ITEM
            if sprite == SpriteType.BULLET_BILL or sprite == SpriteType.SHELL or sprite == SpriteType.GOOMBA or\
                sprite == SpriteType.GOOMBA_WINGED or sprite == SpriteType.GREEN_KOOPA or sprite == SpriteType.GREEN_KOOPA_WINGED or\
                sprite == SpriteType.RED_KOOPA or sprite == SpriteType.RED_KOOPA_WINGED:
                return MarioForwardModel.OBS_STOMPABLE_ENEMY
            if sprite == SpriteType.SPIKY or sprite == SpriteType.SPIKY_WINGED or sprite == SpriteType.ENEMY_FLOWER:
                return MarioForwardModel.OBS_NONSTOMPABLE_ENEMY
            return MarioForwardModel.OBS_NONE
        if detail == 2:
            if sprite == SpriteType.FIREBALL or sprite == SpriteType.MARIO or sprite == SpriteType.MUSHROOM or\
                sprite == SpriteType.LIFE_MUSHROOM or sprite == SpriteType.FIRE_FLOWER:
                return MarioForwardModel.OBS_NONE
            return MarioForwardModel.OBS_ENEMY
        return MarioForwardModel.OBS_UNDEF

    def getBlockValueGeneralization(tile, detail):
        if tile == 0:
            return MarioForwardModel.OBS_NONE
        
        if detail == 0:
            # invisble blocks
            if tile == 48 or tile == 49:
                return MarioForwardModel.OBS_NONE
            # brick blocks
            if tile == 6 or tile == 7 or tile == 50 or tile == 51:
                return MarioForwardModel.OBS_BRICK
            # ? blocks
            if tile == 8 or tile == 11:
                return MarioForwardModel.OBS_QUESTION_BLOCK 
            return tile + MarioForwardModel.OBS_SCENE_SHIFT
        if detail == 1:
            # invisble blocks and body for jumpthrough platform
            if tile == 48 or tile == 49 or tile == 47:
                return MarioForwardModel.OBS_NONE
            # solid blocks
            if tile == 1 or tile == 2 or tile == 14:
                return MarioForwardModel.OBS_SOLID
            # bullet bill blocks
            if tile == 3 or tile == 4 or tile == 5:
                return MarioForwardModel.OBS_CANNON
            # pipe blocks
            if tile == 18 or tile == 19 or tile == 20 or tile == 21:
                return MarioForwardModel.OBS_PIPE
            # brick blocks
            if tile == 6 or tile == 7 or tile == 50 or tile == 51:
                return MarioForwardModel.OBS_BRICK
            # ? blocks
            if tile == 8 or tile == 11:
                return MarioForwardModel.OBS_QUESTION_BLOCK
            # coin
            if tile == 15:
                return MarioForwardModel.OBS_COIN
            # Jump through platforms
            if tile == 44 or tile == 45 or tile == 46:
                return MarioForwardModel.OBS_PLATFORM
            return MarioForwardModel.OBS_NONE
        if detail == 2:
            #invisble blocks and body for jumpthrough platform
            if tile == 48 or tile == 49 or tile == 47:
                return MarioForwardModel.OBS_NONE
            return MarioForwardModel.OBS_SCENE_OBJECT
        return MarioForwardModel.OBS_UNDEF

    # The width of the observation grid
    obsGridWidth = MarioGame.tileWidth
    # The height of the observation grid
    obsGridHeight = MarioGame.tileHeight

    def __init__(self, world):
        self._world = world
        # stats
        self._fallKill = 0
        self._stompKill = 0
        self._fireKill = 0
        self._shellKill = 0
        self._mushrooms = 0
        self._flowers = 0
        self._breakBlock = 0

    def clone(self):
        model = MarioForwardModel(self._world.clone())
        model._fallKill = self._fallKill
        model._stompKill = self._stompKill
        model._fireKill = self._fireKill
        model._shellKill = self._shellKill
        model._mushrooms = self._mushrooms
        model._flowers = self._flowers
        model._breakBlock = self._breakBlock
        return model

    def advance(self, actions):
        MarioForwardModel.maxMoves -= 1
        self._world.update(actions)
        for e in self._world.lastFrameEvents:
            if e.getEventType() == EventType.FIRE_KILL.value:
                self._fireKill += 1
            if e.getEventType() == EventType.STOMP_KILL.value:
                self._stompKill += 1
            if e.getEventType() == EventType.FALL_KILL.value:
                self._fallKill += 1
            if e.getEventType() == EventType.SHELL_KILL.value:
                self._shellKill += 1
            if e.getEventType() == EventType.COLLECT.value:
                if e.getEventParam() == SpriteType.FIRE_FLOWER.value:
                    self._flowers += 1
                if e.getEventParam() == SpriteType.MUSHROOM.value: 
                    self._mushrooms += 1
            if e.getEventType() == EventType.BUMP.value and e.getEventParam() == MarioForwardModel.OBS_BRICK and\
                    e.getMarioState() > 0:
                self._breakBlock += 1

    def getGameStatus(self):
        return self._world.gameStatus

    def getCompletionPercentage(self):
        return self._world.mario.x / (self._world.level.exitTileX * 16)

    def getLevelFloatDimensions(self):
        return [self._world.level.width, self._world.level.height]

    def getRemainingTime(self):
        return self._world.currentTimer
    
    def getRemainingMoves(self):
        return MarioForwardModel.maxMoves

    def getMarioFloatPos(self):
        return [self._world.mario.x, self._world.mario.y]
    

    def getMarioFloatVelocity(self):
        return [self._world.mario.xa, self._world.mario.ya]

    def getMarioCanJumpHigher(self):
        return self._world.mario.jumpTime > 0

    def getMarioMode(self):
        value = 0
        if self._world.mario.isLarge:
            value = 1
        if self._world.mario.isFire:
            value = 2
        return value

    def isMarioOnGround(self):
        return self._world.mario.onGround

    def mayMarioJump(self):
        return self._world.mario.mayJump

    def getEnemiesFloatPos(self):
        enemiesAlive = self._world.getEnemies()
        enemyPos = []
        for  i  in range(len(enemiesAlive)):
            enemyPos.append(enemiesAlive[i].type.value)
            enemyPos.append(enemiesAlive[i].x)
            enemyPos.append(enemiesAlive[i].y)
        return enemyPos

    def getKillsTotal(self):
        return self._fallKill + self._fireKill + self._shellKill + self._stompKill

    def getKillsByFire(self):
        return self._fireKill

    def getKillsByStomp(self):
        return self._stompKill

    def getKillsByShell(self):
        return self._shellKill

    def getKillsByFall(self):
        return self._fallKill

    def getNumLives(self):
        return self._world.lives

    def getNumCollectedMushrooms(self):
        return self._mushrooms

    def getNumCollectedFireflower(self):
        return self._flowers

    def getNumCollectedCoins(self):
        return self._world.coins

    def getNumDestroyedBricks(self):
        return self._breakBlock

    def getMarioScreenTilePos(self):
        return [int((self._world.mario.x - self._world.cameraX) / 16), int(self._world.mario.y / 16)]

    def getScreenCompleteObservation(self, sceneDetail = 1, enemyDetail = 0):
        return self._world.getMergedObservation(self._world.cameraX + MarioGame.width / 2, MarioGame.height / 2,
                                                sceneDetail, enemyDetail)

    def getScreenEnemiesObservation(self, detail = 0):
        return self._world.getEnemiesObservation(self._world.cameraX + MarioGame.width / 2, MarioGame.height / 2, detail)
    
    def getScreenSceneObservation(self, detail = 1):
        return self._world.getSceneObservation(self._world.cameraX + MarioGame.width / 2, MarioGame.height / 2, detail)

    def getMarioCompleteObservation(self, sceneDetail = 1, enemyDetail = 0):
        return self._world.getMergedObservation(self._world.mario.x, self._world.mario.y, sceneDetail, enemyDetail)

    def getMarioEnemiesObservation(self, detail = 0):
        return self._world.getEnemiesObservation(self._world.mario.x, self._world.mario.y, detail)

    def getMarioSceneObservation(self, detail = 1):
        return self._world.getSceneObservation(self._world.mario.x, self._world.mario.y, detail)
    
class MarioResult:
    def __init__(self, world, gameEvents, agentEvents):
       self._world = world
       self._gameEvents = gameEvents
       self._agentEvents = agentEvents

    def getGameStatus(self):
        return self._world.gameStatus

    def getCompletionPercentage(self):
        return self._world.mario.x / (self._world.level.exitTileX * 16)

    def getRemainingTime(self):
        return self._world.currentTimer

    def getMarioMode(self):
        value = 0
        if self._world.mario.isLarge:
            value = 1
        if self._world.mario.isFire:
            value = 2
        return value

    def getGameEvents(self):
        return self._gameEvents

    def getAgentEvents(self):
        return self._agentEvents

    def getKillsTotal(self):
        kills = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.STOMP_KILL.value or e.getEventType() == EventType.FIRE_KILL.value or\
                    e.getEventType() == EventType.FALL_KILL.value or e.getEventType() == EventType.SHELL_KILL.value:
                kills += 1
        return kills

    def getKillsByFire(self):
        kills = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.FIRE_KILL.value:
                kills += 1
        return kills

    def getKillsByStomp(self):
        kills = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.STOMP_KILL.value:
                kills += 1
        return kills

    def getKillsByShell(self):
        kills = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.SHELL_KILL.value:
                kills += 1
        return kills

    def getMarioNumKills(self, enemyType):
        kills = 0
        for e in self._gameEvents:
            if (e.getEventType() == EventType.SHELL_KILL.value or\
                e.getEventType() == EventType.FIRE_KILL.value or\
                e.getEventType() == EventType.STOMP_KILL.value) and e.getEventParam() == enemyType:
                kills += 1
        return kills

    def getMarioNumHurts(self):
        hurt = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.HURT.value:
                hurt += 1
        return hurt

    def getNumBumpQuestionBlock(self):
        bump = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.BUMP.value and e.getEventParam() == MarioForwardModel.OBS_QUESTION_BLOCK:
                bump += 1
        return bump

    def getNumBumpBrick(self):
        bump = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.BUMP.value and e.getEventParam() == MarioForwardModel.OBS_BRICK:
                bump += 1
        return bump

    def getKillsByFall(self):
        kills = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.FALL_KILL.value:
                kills += 1
        return kills

    def getNumJumps(self):
        jumps = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.JUMP.value:
                jumps += 1
        return jumps

    def getMaxXJump(self):
        maxXJump = 0
        startX = -100
        for e in self._gameEvents:
            if e.getEventType() == EventType.JUMP.value:
                startX = e.getMarioX()
            if e.getEventType() == EventType.LAND.value:
                if abs(e.getMarioX() - startX) > maxXJump:
                    maxXJump = abs(e.getMarioX() - startX)
        return maxXJump

    def getMaxJumpAirTime(self):
        maxAirJump = 0
        startTime = -100
        for e in self._gameEvents:
            if e.getEventType() == EventType.JUMP.value:
                startTime = e.getTime()
            if e.getEventType() == EventType.LAND.value:
                if e.getTime() - startTime > maxAirJump:
                    maxAirJump = e.getTime() - startTime
        return maxAirJump

    def getCurrentLives(self):
        return self._world.lives

    def getCurrentCoins(self):
        return self._world.coins

    def getNumCollectedMushrooms(self):
        collect = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.COLLECT.value and e.getEventParam() == SpriteType.MUSHROOM.value:
                collect += 1
        return collect

    def getNumCollectedFireflower(self):
        collect = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.COLLECT.value and e.getEventParam() == SpriteType.FIRE_FLOWER.value:
                collect += 1
        return collect

    def getNumCollectedTileCoins(self):
        collect = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.COLLECT.value and e.getEventParam() == MarioForwardModel.OBS_COIN:
                collect += 1
        return collect

    def getNumDestroyedBricks(self):
        bricks = 0
        for e in self._gameEvents:
            if e.getEventType() == EventType.BUMP.value and\
                e.getEventParam() == MarioForwardModel.OBS_BRICK and e.getMarioState() > 0:
                bricks += 1
        return bricks
    
def currentTimeMillis():
    return round(time.time() * 1000)
    
class MarioLevel:
    def __init__(self, level):
        self.width = MarioGame.width
        self.tileWidth = MarioGame.width / 16
        self.height = MarioGame.height
        self.tileHeight = MarioGame.height / 16
        self.totalCoins = 0
        self.marioTileX = 0
        self.marioTileY = 0
        self.exitTileX = 0
        self.exitTileY = 0

        self._levelTiles = []
        self._spriteTemplates = []
        self._lastSpawnTime = []

        if len(level.strip()) == 0:
            self.tileWidth = 0
            self.width = 0
            self.tileHeight = 0
            self.height = 0
            return

        lines = level.split("\n")
        self.tileWidth = len(lines[0])
        self.width = self.tileWidth * 16
        self.tileHeight = len(lines)
        self.height = self.tileHeight * 16

        for x in range(len(lines[0])):            
            self._levelTiles.append([])
            self._spriteTemplates.append([])
            self._lastSpawnTime.append([])
            for _ in range(len(lines)):
                self._levelTiles[x].append(0)
                self._spriteTemplates[x].append(SpriteType.NONE)
                self._lastSpawnTime[x].append(-40)

        marioLocInit = False
        exitLocInit = False
        for y in range(len(lines)):
            for x in range(len(lines[y])):
                c = lines[y][x]
                if c == 'M':
                    self.marioTileX = x
                    self.marioTileY = y
                    marioLocInit = True
                    continue
                if c == 'F':
                    self.exitTileX = x
                    self.exitTileY = y
                    exitLocInit = True
                    continue
                if c == 'y':
                    self._spriteTemplates[x][y] = SpriteType.SPIKY
                    continue
                if c == 'Y':
                    self._spriteTemplates[x][y] = SpriteType.SPIKY_WINGED
                    continue
                if c == 'E' or c == 'g':
                    self._spriteTemplates[x][y] = SpriteType.GOOMBA
                    continue
                if c == 'G':
                    self._spriteTemplates[x][y] = SpriteType.GOOMBA_WINGED
                    continue
                if c == 'k':
                    self._spriteTemplates[x][y] = SpriteType.GREEN_KOOPA
                    continue
                if c == 'K':
                    self._spriteTemplates[x][y] = SpriteType.GREEN_KOOPA_WINGED
                    continue
                if c == 'r':
                    self._spriteTemplates[x][y] = SpriteType.RED_KOOPA
                    continue
                if c == 'R':
                    self._spriteTemplates[x][y] = SpriteType.RED_KOOPA_WINGED
                    continue
                if c == 'X':
                    self._levelTiles[x][y] = 1
                    continue
                if c == '#':
                    self._levelTiles[x][y] = 2
                    continue
                if c == '%':
                    tempIndex = 0
                    if x > 0 and lines[y][x - 1] == '%':
                        tempIndex += 2
                    if x < len(self._levelTiles) - 1 and lines[y][x + 1] == '%':
                        tempIndex += 1
                    self._levelTiles[x][y] = 43 + tempIndex
                    continue
                if c == '|':
                    self._levelTiles[x][y] = 47
                    continue
                if c == '*':
                    tempIndex = 0
                    if y > 0 and lines[y - 1][x] == '*':
                        tempIndex += 1
                    if y > 1 and lines[y - 2][x] == '*':
                        tempIndex += 1
                    self._levelTiles[x][y] = 3 + tempIndex
                    continue
                if c == 'B':
                    self._levelTiles[x][y] = 3
                    continue
                if c == 'b':
                    tempIndex = 0
                    if y > 1 and lines[y - 2][x] == 'B':
                        tempIndex += 1
                    self._levelTiles[x][y] = 4 + tempIndex
                    continue
                if c == '?' or c == '@':
                    self._levelTiles[x][y] = 8
                    continue
                if c == 'Q' or c == '!':
                    self.totalCoins += 1
                    self._levelTiles[x][y] = 11
                    continue
                if c == '1':
                    self._levelTiles[x][y] = 48
                    continue
                if c == '2':
                    self.totalCoins += 1
                    self._levelTiles[x][y] = 49
                    continue
                if c == 'D':
                    self._levelTiles[x][y] = 14
                    continue
                if c == 'S':
                    self._levelTiles[x][y] = 6
                    continue
                if c == 'C':
                    self.totalCoins += 1
                    self._levelTiles[x][y] = 7
                    continue
                if c == 'U':
                    self._levelTiles[x][y] = 50
                    continue
                if c == 'L':
                    self._levelTiles[x][y] = 51
                    continue
                if c == 'o':
                    self.totalCoins += 1
                    self._levelTiles[x][y] = 15
                    continue
                if c == 't':
                    tempIndex = 0
                    singlePipe = False
                    if x < len(lines[y]) - 1 and lines[y][x + 1].lower() != 't' and\
                            x > 0 and lines[y][x - 1].lower() != 't':
                            singlePipe = True
                    if x > 0 and (self._levelTiles[x - 1][y] == 18 or self._levelTiles[x - 1][y] == 20):
                        tempIndex += 1
                    if y > 0 and lines[y - 1][x].lower() == 't':
                        if singlePipe:
                            tempIndex += 1
                        else:
                            tempIndex += 2
                        
                    if singlePipe:
                        self._levelTiles[x][y] = 52 + tempIndex
                    else:
                        self._levelTiles[x][y] = 18 + tempIndex
                    continue
                if c == 'T':
                    tempIndex = 0
                    singlePipe = False
                    if x < len(lines[y]) - 1 and lines[y][x + 1].lower() != 't' and\
                            x > 0 and lines[y][x - 1].lower() != 't':
                            singlePipe = True
                    if x > 0 and (self._levelTiles[x - 1][y] == 18 or self._levelTiles[x - 1][y] == 20):
                        tempIndex += 1
                    if y > 0 and lines[y - 1][x].lower() == 't':
                        if singlePipe:
                            tempIndex += 1
                        else:
                            tempIndex += 2
                        
                    if singlePipe:
                        self._levelTiles[x][y] = 52 + tempIndex
                    else:
                        if tempIndex == 0:
                            self._spriteTemplates[x][y] = SpriteType.ENEMY_FLOWER
                        self._levelTiles[x][y] = 18 + tempIndex
                    continue
                if c == '<':
                    self._levelTiles[x][y] = 18
                    continue
                if c == '>':
                    self._levelTiles[x][y] = 19
                    continue
                if c == '[':
                    self._levelTiles[x][y] = 20
                    continue
                if c == ']':
                    self._levelTiles[x][y] = 21
                    continue
        if not marioLocInit:
            self.marioTileX = 0
            self.marioTileY = self._findFirstFloor(lines, self.marioTileX)
        if not exitLocInit:
            self.exitTileX = len(lines[0]) - 1
            self.exitTileY = self._findFirstFloor(lines, self.exitTileX)
        for y in range(self.exitTileY, max(1, self.exitTileY-11),-1):
            self._levelTiles[self.exitTileX][y] = 40
        self._levelTiles[self.exitTileX][max(1, self.exitTileY - 11)] = 39

    def clone(self):
        level = MarioLevel("")
        level.width = self.width
        level.height = self.height
        level.tileWidth = self.tileWidth
        level.tileHeight = self.tileHeight
        level.totalCoins = self.totalCoins
        level.marioTileX = self.marioTileX
        level.marioTileY = self.marioTileY
        level.exitTileX = self.exitTileX
        level.exitTileY = self.exitTileY
        level._levelTiles = []
        level._lastSpawnTime = []
        for x in range(len(self._levelTiles)):
            level._levelTiles.append([])
            level._lastSpawnTime.append([])
            for y in range(len(self._levelTiles[x])):
                level._levelTiles[x].append(self._levelTiles[x][y])
                level._lastSpawnTime[x].append(self._lastSpawnTime[x][y])
        level._spriteTemplates = self._spriteTemplates
        return level

    def isBlocking(self, xTile, yTile, xa, ya):
        block = self.getBlock(xTile, yTile)
        features = TileFeature.getTileType(block)
        blocking = (TileFeature.BLOCK_ALL in features)
        blocking |= (ya < 0) and (TileFeature.BLOCK_UPPER in features)
        blocking |= (ya > 0) and (TileFeature.BLOCK_LOWER in features)
        return blocking

    def getBlock(self, xTile, yTile):
        if xTile < 0:
            xTile = 0
        if xTile > self.tileWidth - 1:
            xTile = self.tileWidth - 1
        if yTile < 0 or yTile > self.tileHeight - 1:
            return 0
        return self._levelTiles[xTile][yTile]

    def setBlock(self, xTile, yTile, index):
        if xTile < 0 or yTile < 0 or xTile > self.tileWidth - 1 or yTile > self.tileHeight - 1:
            return
        self._levelTiles[xTile][yTile] = index

    def getSpriteType(self, xTile, yTile):
        if xTile < 0 or yTile < 0 or xTile >= self.tileWidth or yTile >= self.tileHeight:
            return SpriteType.NONE
        return self._spriteTemplates[xTile][yTile]

    def getLastSpawnTick(self, xTile, yTile):
        if xTile < 0 or yTile < 0 or xTile > self.tileWidth - 1 or yTile > self.tileHeight - 1:
            return 0
        return self._lastSpawnTime[xTile][yTile]

    def setLastSpawnTick(self, xTile, yTile, tick):
        if xTile < 0 or yTile < 0 or xTile > self.tileWidth - 1 or yTile > self.tileHeight - 1:
            return
        self._lastSpawnTime[xTile][yTile] = tick

    def getSpriteCode(self, xTile, yTile):
        return f"{xTile}_{yTile}_{self.getSpriteType(xTile, yTile).value}"

    def _isSolid(self, c):
        return c == 'X' or c == '#' or c == '@' or c == '!' or c == 'B' or c == 'C' or\
                c == 'Q' or c == '<' or c == '>' or c == '[' or c == ']' or c == '?' or\
                c == 'S' or c == 'U' or c == 'D' or c == '%' or c == 't' or c == 'T'

    def _findFirstFloor(self, lines, x):
        skipLines = True
        for i in range(len(lines)-1, -1, -1):
            c = lines[i][x]
            if self._isSolid(c):
                skipLines = False
                continue
            if not skipLines and not self._isSolid(c):
                return i
        return -1

    def update(self, cameraX, cameraY):
        return
    
class MarioWorld:
    def __init__(self, killEvents):
        self.pauseTimer = 0
        self.gameStatus = GameStatus.RUNNING
        self.fireballsOnScreen = 0
        self.currentTimer = -1
        self.cameraX = 0.0
        self.cameraY = 0.0
        self.mario = None
        self.level = None
        self.currentTick = 0
        self.coins = 0
        self.lives = 0
        self.lastFrameEvents = []

        self._killEvents = killEvents
        self._sprites = []
        self._shellsToCheck = []
        self._fireballsToCheck = []
        self._addedSprites = []
        self._removedSprites = []

    def initializeLevel(self, level, timer):
        self.currentTimer = timer
        self.level = MarioLevel(level)

        self.mario = Mario(self.level.marioTileX * 16, self.level.marioTileY * 16)
        self.mario.alive = True
        self.mario.world = self
        self._sprites.append(self.mario)

    def getEnemies(self):
        enemies = []
        for sprite in self._sprites:
            if (self._isEnemy(sprite)):
                enemies.add(sprite)
        return enemies

    def clone(self):
        world = MarioWorld(self._killEvents)
        world.cameraX = self.cameraX
        world.cameraY = self.cameraY
        world.fireballsOnScreen = self.fireballsOnScreen
        world.gameStatus = self.gameStatus
        world.pauseTimer = self.pauseTimer
        world.currentTimer = self.currentTimer
        world.currentTick = self.currentTick
        world.level = self.level.clone()
        for sprite in self._sprites:
            cloneSprite = sprite.clone()
            cloneSprite.world = world
            if cloneSprite.type == SpriteType.MARIO:
                world.mario = cloneSprite
            world._sprites.append(cloneSprite)
        if world.mario == None:
            world.mario = self.mario.clone()
        world.coins = self.coins
        world.lives = self.lives
        return world

    def addEvent(self, eventType, eventParam):
        marioState = 0
        if (self.mario.isLarge):
            marioState = 1
        if (self.mario.isFire):
            marioState = 2
        self.lastFrameEvents.append(MarioEvent(eventType, eventParam, self.mario.x, self.mario.y, marioState, self.currentTick))

    def addSprite(self, sprite):
        self._addedSprites.append(sprite)
        sprite.alive = True
        sprite.world = self
        sprite.added()
        sprite.update()

    def removeSprite(self, sprite):
        self._removedSprites.append(sprite)
        sprite.alive = False
        sprite.removed()
        sprite.world = None

    def checkShellCollide(self, shell):
        self._shellsToCheck.append(shell)

    def checkFireballCollide(self, fireball):
        self._fireballsToCheck.append(fireball)

    def win(self):
        self.addEvent(EventType.WIN, 0)
        self.gameStatus = GameStatus.WIN

    def lose(self):
        self.addEvent(EventType.LOSE, 0)
        self.gameStatus = GameStatus.LOSE
        self.mario.alive = False

    def timeout(self):
        self.gameStatus = GameStatus.TIME_OUT
        self.mario.alive = False

    def getSceneObservation(self, centerX, centerY, detail):
        ret = np.zeros((int(MarioGame.tileWidth), int(MarioGame.tileHeight)), dtype=int)
        centerXInMap = int(centerX / 16)
        centerYInMap = int(centerY / 16)
        
        obsY = 0
        for y in range(int(centerYInMap - MarioGame.tileHeight / 2), int(centerYInMap + MarioGame.tileHeight / 2)):
            obsX = 0
            for x in range(int(centerXInMap - MarioGame.tileWidth / 2), int(centerXInMap + MarioGame.tileWidth / 2)):
                currentX = x
                if currentX < 0:
                    currentX = 0
                if currentX > self.level.tileWidth - 1:
                    currentX = self.level.tileWidth - 1
                currentY = y
                if currentY < 0:
                    currentY = 0
                if currentY > self.level.tileHeight - 1:
                    currentY = self.level.tileHeight - 1
                ret[obsX][obsY] = MarioForwardModel.getBlockValueGeneralization(self.level.getBlock(currentX, currentY), detail)
                obsX += 1
            obsY += 1
        return ret

    def getEnemiesObservation(self, centerX, centerY, detail):
        ret = np.zeros((int(MarioGame.tileWidth), int(MarioGame.tileHeight)), dtype=int)
        centerXInMap = int(centerX / 16)
        centerYInMap = int(centerY / 16)

        for sprite in self._sprites:
            if sprite.type == SpriteType.MARIO:
                continue
            if sprite.getMapX() >= 0 and\
                    sprite.getMapX() > centerXInMap - MarioGame.tileWidth / 2 and\
                    sprite.getMapX() < centerXInMap + MarioGame.tileWidth / 2 and\
                    sprite.getMapY() >= 0 and\
                    sprite.getMapY() > centerYInMap - MarioGame.tileHeight / 2 and\
                    sprite.getMapY() < centerYInMap + MarioGame.tileHeight / 2:
                obsX = int(sprite.getMapX() - centerXInMap + MarioGame.tileWidth / 2)
                obsY = int(sprite.getMapY() - centerYInMap + MarioGame.tileHeight / 2)
                ret[obsX][obsY] = MarioForwardModel.getSpriteTypeGeneralization(sprite.type.value, detail)
        return ret

    def getMergedObservation(self, centerX, centerY, sceneDetail, enemiesDetail):
        ret = np.zeros((int(MarioGame.tileWidth), int(MarioGame.tileHeight)), dtype=int)
        centerXInMap = int(centerX / 16)
        centerYInMap = int(centerY / 16)

        obsY = 0
        for y in range(int(centerYInMap - MarioGame.tileHeight / 2), int(centerYInMap + MarioGame.tileHeight / 2)):
            obsX = 0
            for x in range(int(centerXInMap - MarioGame.tileWidth / 2), int(centerXInMap + MarioGame.tileWidth / 2)):
                currentX = x
                if currentX < 0:
                    currentX = 0
                if currentX > self.level.tileWidth - 1:
                    currentX = self.level.tileWidth - 1
                currentY = y
                if currentY < 0:
                    currentY = 0
                if currentY > self.level.tileHeight - 1:
                    currentY = self.level.tileHeight - 1
                ret[obsX][obsY] = MarioForwardModel.getBlockValueGeneralization(self.level.getBlock(x, y), sceneDetail)
                obsX += 1
            obsY += 1

        for sprite in self._sprites:
            if sprite.type == SpriteType.MARIO:
                continue
            if sprite.getMapX() >= 0 and\
                    sprite.getMapX() > centerXInMap - MarioGame.tileWidth / 2 and\
                    sprite.getMapX() < centerXInMap + MarioGame.tileWidth / 2 and\
                    sprite.getMapY() >= 0 and\
                    sprite.getMapY() > centerYInMap - MarioGame.tileHeight / 2 and\
                    sprite.getMapY() < centerYInMap + MarioGame.tileHeight / 2:
                obsX = int(sprite.getMapX() - centerXInMap + MarioGame.tileWidth / 2)
                obsY = int(sprite.getMapY() - centerYInMap + MarioGame.tileHeight / 2)
                tmp = MarioForwardModel.getSpriteTypeGeneralization(sprite.type.value, enemiesDetail)
                if tmp != SpriteType.NONE.value:
                    ret[obsX][obsY] = tmp
        return ret

    def _isEnemy(self, sprite):
        return isinstance(sprite, Enemy) or isinstance(sprite, FlowerEnemy) or isinstance(sprite, BulletBill)

    def update(self,  actions):
        if self.gameStatus != GameStatus.RUNNING:
            return
        if self.pauseTimer > 0:
            self.pauseTimer -= 1
            return

        if self.currentTimer > 0:
            self.currentTimer -= 30
            if self.currentTimer <= 0:
                self.currentTimer = 0
                self.timeout()
                return
        
        self.currentTick += 1
        self.cameraX = self.mario.x - MarioGame.width / 2
        if self.cameraX + MarioGame.width > self.level.width:
            self.cameraX = self.level.width - MarioGame.width
        if self.cameraX < 0:
            self.cameraX = 0
        self.cameraY = self.mario.y - MarioGame.height / 2
        if self.cameraY + MarioGame.height > self.level.height:
            self.cameraY = self.level.height - MarioGame.height
        if self.cameraY < 0:
            self.cameraY = 0

        self.lastFrameEvents.clear()

        self.fireballsOnScreen = 0
        for sprite in self._sprites:
            if sprite.x < self.cameraX - 64 or sprite.x > self.cameraX + MarioGame.width + 64 or sprite.y > self.level.height + 32:
                if sprite.type == SpriteType.MARIO:
                    self.lose()
                self.removeSprite(sprite)
                if self._isEnemy(sprite) and sprite.y > MarioGame.height + 32:
                    self.addEvent(EventType.FALL_KILL, sprite.type.value)
                continue
            if sprite.type == SpriteType.FIREBALL:
                self.fireballsOnScreen += 1
        self.level.update(int(self.cameraX), int(self.cameraY))

        for x in range(int(self.cameraX / 16) - 1, int((self.cameraX + MarioGame.width) / 16) + 2):
            for y in range(int(self.cameraY / 16)-1, int((self.cameraY + MarioGame.height) / 16) + 2):
                dir = 0
                if x * 16 + 8 > self.mario.x + 16:
                    dir = -1
                if x * 16 + 8 < self.mario.x - 16:
                    dir = 1

                type = self.level.getSpriteType(x, y)
                if (type != SpriteType.NONE):
                    spriteCode = self.level.getSpriteCode(x, y)
                    found = False
                    for sprite in self._sprites:
                        if sprite.initialCode == spriteCode:
                            found = True
                            break
                    if not found:
                        if self.level.getLastSpawnTick(x, y) != self.currentTick - 1:
                            sprite = spawnSprite(type, x, y, dir)
                            sprite.initialCode = spriteCode
                            self.addSprite(sprite)
                    self.level.setLastSpawnTick(x, y, self.currentTick)

                if dir != 0:
                    features = TileFeature.getTileType(self.level.getBlock(x, y))
                    if TileFeature.SPAWNER in features:
                        if self.currentTick % 100 == 0:
                            self.addSprite(BulletBill(x * 16 + 8 + dir * 8, y * 16 + 15, dir))

        self.mario.actions = actions
        for sprite in self._sprites:
            if not sprite.alive:
                continue
            sprite.update()
        for sprite in self._sprites:
            if not sprite.alive:
                continue
            sprite.collideCheck()

        for shell in self._shellsToCheck:
            for sprite in self._sprites:
                if sprite != shell and shell.alive and sprite.alive:
                    if sprite.shellCollideCheck(shell):
                        self.removeSprite(sprite)
        self._shellsToCheck.clear()

        for fireball in self._fireballsToCheck:
            for sprite in self._sprites:
                if sprite != fireball and fireball.alive and sprite.alive:
                    if sprite.fireballCollideCheck(fireball):
                        self.removeSprite(fireball)
        self._fireballsToCheck.clear()

        for sprite in self._addedSprites:
            self._sprites.append(sprite)
        for sprite in self._removedSprites:
            self._sprites.remove(sprite)
        self._addedSprites.clear()
        self._removedSprites.clear()

        if self._killEvents != None:
            for k in self._killEvents:
                if k in self.lastFrameEvents:
                    self.lose()

    def bump(self, xTile, yTile, canBreakBricks):
        block = self.level.getBlock(xTile, yTile)
        features = TileFeature.getTileType(block)

        if TileFeature.BUMPABLE in features:
            self.bumpInto(xTile, yTile - 1)
            self.addEvent(EventType.BUMP, MarioForwardModel.OBS_QUESTION_BLOCK)
            self.level.setBlock(xTile, yTile, 14)

            if TileFeature.SPECIAL in features:
                if not self.mario.isLarge:
                    self.addSprite(Mushroom(xTile * 16 + 9, yTile * 16 + 8))
                else:
                    self.addSprite(FireFlower(xTile * 16 + 9, yTile * 16 + 8))
            elif TileFeature.LIFE in features:
                self.addSprite(LifeMushroom(xTile * 16 + 9, yTile * 16 + 8))
            else:
                self.mario.collectCoin()

        if TileFeature.BREAKABLE in features:
            self.bumpInto(xTile, yTile - 1)
            if canBreakBricks:
                self.addEvent(EventType.BUMP, MarioForwardModel.OBS_BRICK)
                self.level.setBlock(xTile, yTile, 0)

    def bumpInto(self, xTile, yTile):
        block = self.level.getBlock(xTile, yTile)
        if TileFeature.PICKABLE in TileFeature.getTileType(block):
            self.addEvent(EventType.COLLECT, block)
            self.mario.collectCoin()
            self.level.setBlock(xTile, yTile, 0)

        for sprite in self._sprites:
            sprite.bumpCheck(xTile, yTile)