from .helper import SpriteType, EventType, TileFeature, MarioActions

def spawnSprite(type, xTile, yTile, dir):
    if type == SpriteType.ENEMY_FLOWER:
        return FlowerEnemy(xTile * 16 + 17, yTile * 16 + 18)
    return Enemy(xTile * 16 + 8, yTile * 16 + 15, dir, type)

class MarioSprite:
    def __init__(self, x, y, type):
        self.initialCode = ""
        self.x = x
        self.y = y
        self.xa = 0
        self.ya = 0
        self.facing = 1
        self.alive = True
        self.world = None
        self.width = 16
        self.height = 16
        self.type = type

    def clone(self):
        return None

    def added(self):
        return

    def removed(self):
        return

    def getMapX(self):
        return int(self.x / 16)

    def getMapY(self):
        return int(self.y / 16)

    def update(self):
        return

    def collideCheck(self):
        return

    def bumpCheck(self, xTile, yTile):
        return

    def shellCollideCheck(self, shell):
        return False

    def release(self, mario):
        return

    def fireballCollideCheck(self, fireball):
        return False

class Enemy(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89

    def __init__(self, x, y, dir, type):
        MarioSprite.__init__(self, x, y, type)

        self._onGround = False
        self._avoidCliffs = True
        self._winged = True
        self._noFireballDeath = False

        self.width = 4
        self.height = 24
        if self.type != SpriteType.RED_KOOPA and self.type != SpriteType.GREEN_KOOPA and\
            self.type != SpriteType.RED_KOOPA_WINGED and self.type != SpriteType.GREEN_KOOPA_WINGED:
            self.height = 12
        self._winged = self.type.value % 2 == 1
        self._avoidCliffs = self.type == SpriteType.RED_KOOPA or self.type == SpriteType.RED_KOOPA_WINGED
        self._noFireballDeath = self.type == SpriteType.SPIKY or self.type == SpriteType.SPIKY_WINGED
        self.facing = dir
        if self.facing == 0:
            self.facing = 1

    def clone(self):
        e = Enemy(self.x, self.y, self.facing, self.type)
        e.xa = self.xa
        e.ya = self.ya
        e.initialCode = self.initialCode
        e.width = self.width
        e.height = self.height
        e._onGround = self._onGround
        e._winged = self._winged
        e._avoidCliffs = self._avoidCliffs
        e._noFireballDeath = self._noFireballDeath
        return e

    def collideCheck(self):
        if not self.alive:
            return

        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -self.width * 2 - 4 and xMarioD < self.width * 2 + 4:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                if self.type != SpriteType.SPIKY and type != SpriteType.SPIKY_WINGED and type != SpriteType.ENEMY_FLOWER and\
                        self.world.mario.ya > 0 and yMarioD <= 0 and (not self.world.mario.onGround or not self.world.mario.wasOnGround):
                    self.world.mario.stomp(self)
                    if self._winged:
                        self._winged = False
                        self.ya = 0
                    else:
                        if type == SpriteType.GREEN_KOOPA or type == SpriteType.GREEN_KOOPA_WINGED:
                            self.world.addSprite(Shell(self.x, self.y, 1, self.initialCode))
                        elif type == SpriteType.RED_KOOPA or type == SpriteType.RED_KOOPA_WINGED:
                            self.world.addSprite(Shell(self.x, self.y, 0, self.initialCode))
                        self.world.addEvent(EventType.STOMP_KILL, self.type.value)
                        self.world.removeSprite(self)
                else:
                    self.world.addEvent(EventType.HURT, self.type.value)
                    self.world.mario.getHurt()

    def update(self):
        if not self.alive:
            return
        sideWaysSpeed = 1.75
        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1

        self.xa = self.facing * sideWaysSpeed

        if not self._move(self.xa, 0):
            self.facing = -self.facing
        self._onGround = False
        self._move(0, self.ya)

        self.ya *= [0.85, 0.95][self._winged]
        if self._onGround:
            self.xa *= Enemy._GROUND_INERTIA
        else:
            self.xa *= Enemy._AIR_INERTIA

        if not self._onGround:
            if self._winged:
                self.ya += 0.6
            else:
                self.ya += 2
        elif self._winged:
            self.ya = -10

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True

            if self._avoidCliffs and self._onGround and\
                    not self.world.level.isBlocking(int((self.x + xa + self.width) / 16), int((self.y) / 16 + 1), xa, 1):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True

            if self._avoidCliffs and self._onGround and\
                    not self.world.level.isBlocking(int((self.x + xa - self.width) / 16), int((self.y) / 16 + 1), xa, 1):
                collide = True

        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.ya = 0
            if ya > 0:
                self.y = int(self.y / 16 + 1) * 16 - 1
                self._onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def _isBlocking(self, _x, _y, xa, ya):
        x = (int) (_x / 16)
        y = (int) (_y / 16)
        if x == int(self.x / 16) and y == int(self.y / 16):
            return False
        blocking = self.world.level.isBlocking(x, y, xa, ya)
        return blocking

    def shellCollideCheck(self, shell):
        if not self.alive:
            return False

        xD = shell.x - self.x
        yD = shell.y - self.y

        if xD > -16 and xD < 16:
            if yD > -self.height and yD < shell.height:
                self.xa = shell.facing * 2
                self.ya = -5
                self.world.addEvent(EventType.SHELL_KILL, self.type.value)
                self.world.removeSprite(self)
                return True
        return False

    def fireballCollideCheck(self, fireball):
        if not self.alive:
            return False

        xD = fireball.x - self.x
        yD = fireball.y - self.y

        if xD > -16 and xD < 16:
            if yD > -self.height and yD < fireball.height:
                if self._noFireballDeath:
                    return True

                self.xa = fireball.facing * 2
                self.ya = -5
                self.world.addEvent(EventType.FIRE_KILL, self.type.value)
                self.world.removeSprite(self)
                return True
        return False

    def bumpCheck(self, xTile, yTile):
        if not self.alive:
            return

        if self.x + self.width > xTile * 16 and self.x - self.width < xTile * 16 + 16 and yTile == int((self.y - 1) / 16):
            self.xa = -self.world.mario.facing * 2
            self.ya = -5
            self.world.removeSprite(self)

class FlowerEnemy(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, x, y, 0, SpriteType.ENEMY_FLOWER)
        self._winged = False
        self.noFireballDeath = False
        self.width = 2
        self._yStart = self.y
        self.ya = -1
        self.y -= 1
        self._waitTime = 0
        for i in range(4):
            self.update()

    def clone(self):
        sprite = FlowerEnemy(self.x, self.y)
        sprite.xa = self.xa
        sprite.ya = self.ya
        sprite.initialCode = self.initialCode
        sprite.width = self.width
        sprite.height = self.height
        sprite._onGround = self._onGround
        sprite._winged = self._winged
        sprite._avoidCliffs = self._avoidCliffs
        sprite._noFireballDeath = self._noFireballDeath
        sprite._yStart = self._yStart
        sprite._waitTime = self._waitTime
        return sprite

    def update(self):
        if not self.alive:
            return

        if self.ya > 0:
            if self.y >= self._yStart:
                self.y = self._yStart
                xd = int(abs(self.world.mario.x - self.x))
                self._waitTime += 1
                if self._waitTime > 40 and xd > 24:
                    self._waitTime = 0
                    self.ya = -1
        elif self.ya < 0:
            if self._yStart - self.y > 20:
                self.y = self._yStart - 20
                self._waitTime += 1
                if self._waitTime > 40:
                    self._waitTime = 0
                    self.ya = 1
        self.y += self.ya

class Mario(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89
    _POWERUP_TIME = 3

    def __init__(self, x, y):
        MarioSprite.__init__(self, x + 8, y + 15, SpriteType.MARIO)
        self.isLarge = False
        self._oldLarge = False
        self.isFire = False
        self._oldFire = False
        self.width = 4
        self.height = 24
        self.onGround = False
        self.wasOnGround = False
        self.isDucking = False
        self.canShoot = False
        self.mayJump = False
        self.actions = None
        self.jumpTime = 0
        self._xJumpSpeed = 0
        self._yJumpSpeed = 0
        self._invulnerableTime = 0
        self._marioFrameSpeed = 0
        self._xJumpStart = -100

    def clone(self):
        sprite = Mario(self.x - 8, self.y - 15)
        sprite.xa = self.xa
        sprite.ya = self.ya
        sprite.initialCode = self.initialCode
        sprite.width = self.width
        sprite.height = self.height
        sprite.facing = self.facing
        sprite.isLarge = self.isLarge
        sprite.isFire = self.isFire
        sprite.wasOnGround = self.wasOnGround
        sprite.onGround = self.onGround
        sprite.isDucking = self.isDucking
        sprite.canShoot = self.canShoot
        sprite.mayJump = self.mayJump
        sprite.actions = []
        for i in range(len(self.actions)):
            sprite.actions.append(self.actions[i])
        sprite._xJumpSpeed = self._xJumpSpeed
        sprite._yJumpSpeed = self._yJumpSpeed
        sprite._invulnerableTime = self._invulnerableTime
        sprite.jumpTime = self.jumpTime
        sprite._xJumpStart = self._xJumpStart
        return sprite

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True
        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.jumpTime = 0
                self.ya = 0
            if ya > 0:
                self.y = int((self.y - 1) / 16 + 1) * 16 - 1
                self.onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def _isBlocking(self, _x, _y, xa, ya):
        xTile = (int) (_x / 16)
        yTile = (int) (_y / 16)
        if xTile == int(self.x / 16) and yTile == int(self.y / 16):
            return False

        blocking = self.world.level.isBlocking(xTile, yTile, xa, ya)
        block = self.world.level.getBlock(xTile, yTile)

        if TileFeature.PICKABLE in TileFeature.getTileType(block):
            self.world.addEvent(EventType.COLLECT, block)
            self.collectCoin()
            self.world.level.setBlock(xTile, yTile, 0)
        if blocking and ya < 0:
            self.world.bump(xTile, yTile, self.isLarge)
        return blocking

    def update(self):
        if not self.alive:
            return

        if self._invulnerableTime > 0:
            self._invulnerableTime -= 1
        self.wasOnGround = self.onGround

        sideWaysSpeed = [0.6, 1.2][self.actions[MarioActions.SPEED.value]]

        if self.onGround:
            self.isDucking = self.actions[MarioActions.DOWN.value] and self.isLarge

        if self.isLarge:
            self.height = [24, 12][self.isDucking]
        else:
            self.height = 12

        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1

        if self.actions[MarioActions.JUMP.value] or (self.jumpTime < 0 and not self.onGround):
            if self.jumpTime < 0:
                self.xa = self._xJumpSpeed
                self.ya = -self.jumpTime * self._yJumpSpeed
                self.jumpTime += 1
            elif self.onGround and self.mayJump:
                self._xJumpSpeed = 0
                self._yJumpSpeed = -1.9
                self.jumpTime = 7
                self.ya = self.jumpTime * self._yJumpSpeed
                self.onGround = False
                if not(self._isBlocking(self.x, self.y - 4 - self.height, 0, -4) or\
                       self._isBlocking(self.x - self.width, self.y - 4 - self.height, 0, -4) or\
                       self._isBlocking(self.x + self.width, self.y - 4 - self.height, 0, -4)):
                    self._xJumpStart = self.x
                    self.world.addEvent(EventType.JUMP, 0)
            elif self.jumpTime > 0:
                self.xa += self._xJumpSpeed
                self.ya = self.jumpTime * self._yJumpSpeed
                self.jumpTime -= 1
        else:
            self.jumpTime = 0

        if self.actions[MarioActions.LEFT.value] and not self.isDucking:
            self.xa -= sideWaysSpeed
            if self.jumpTime >= 0:
                self.facing = -1

        if self.actions[MarioActions.RIGHT.value] and not self.isDucking:
            self.xa += sideWaysSpeed
            if self.jumpTime >= 0:
                self.facing = 1

        if self.actions[MarioActions.SPEED.value] and self.canShoot and self.isFire and self.world.fireballsOnScreen < 2:
            self.world.addSprite(Fireball(self.x + self.facing * 6, self.y - 20, self.facing))

        self.canShoot = not self.actions[MarioActions.SPEED.value]

        self.mayJump = self.onGround and not self.actions[MarioActions.JUMP.value]

        if abs(self.xa) < 0.5:
            self.xa = 0

        self.onGround = False
        self._move(self.xa, 0)
        self._move(0, self.ya)
        if not self.wasOnGround and self.onGround and self._xJumpStart >= 0:
            self.world.addEvent(EventType.LAND, 0)
            self._xJumpStart = -100

        if self.x < 0:
            self.x = 0
            self.xa = 0

        if self.x > self.world.level.exitTileX * 16:
            self.x = self.world.level.exitTileX * 16
            self.xa = 0
            self.world.win()

        self.ya *= 0.85
        if self.onGround:
            self.xa *= Mario._GROUND_INERTIA
        else:
            self.xa *= Mario._AIR_INERTIA

        if not self.onGround:
            self.ya += 3

    def stomp(self, enemy):
        if not self.alive:
            return
        targetY = enemy.y - enemy.height / 2
        self._move(0, targetY - self.y)

        self._xJumpSpeed = 0
        self._yJumpSpeed = -1.9
        self.jumpTime = 8
        self.ya = self.jumpTime * self._yJumpSpeed
        self.onGround = False
        self._invulnerableTime = 1

    def stomp(self, shell):
        if not self.alive:
            return
        targetY = shell.y - shell.height / 2
        self._move(0, targetY - self.y)

        self._xJumpSpeed = 0
        self._yJumpSpeed = -1.9
        self.jumpTime = 8
        self.ya = self.jumpTime * self._yJumpSpeed
        self.onGround = False
        self._invulnerableTime = 1

    def getHurt(self):
        if self._invulnerableTime > 0 or not self.alive:
            return

        if self.isLarge:
            self.world.pauseTimer = 3 * Mario._POWERUP_TIME
            self._oldLarge = self.isLarge
            self._oldFire = self.isFire
            if self.isFire:
                self.isFire = False
            else:
                self.isLarge = False
            self._invulnerableTime = 32
        else:
            if self.world != None:
                self.world.lose()
            
    def getFlower(self):
        if not self.alive:
            return

        if not self.isFire:
            self.world.pauseTimer = 3 * Mario._POWERUP_TIME
            self._oldFire = self.isFire
            self._oldLarge = self.isLarge
            self.isFire = True
            self.isLarge = True
        else:
            self.collectCoin()

    def getMushroom(self):
        if not self.alive:
            return

        if not self.isLarge:
            self.world.pauseTimer = 3 * Mario._POWERUP_TIME
            self._oldFire = self.isFire
            self._oldLarge = self.isLarge
            self.isLarge = True
        else:
            self.collectCoin()

    def kick(self, shell):
        if not self.alive:
            return
        self._invulnerableTime = 1

    def stomp(self, bill):
        if not self.alive:
            return

        targetY = bill.y - bill.height / 2
        self._move(0, targetY - self.y)

        self._xJumpSpeed = 0
        self._yJumpSpeed = -1.9
        self.jumpTime = 8
        self.ya = self.jumpTime * self._yJumpSpeed
        self.onGround = False
        self._invulnerableTime = 1

    def getMarioType(self):
        if self.isFire:
            return "fire"
        if self.isLarge:
            return "large"
        return "small"

    def collect1Up(self):
        if not self.alive:
            return

        self.world.lives += 1

    def collectCoin(self):
        if not self.alive:
            return

        self.world.coins += 1
        if self.world.coins % 100 == 0:
            self.collect1Up()

class BulletBill(MarioSprite):
    def __init__(self, x, y, dir):
        MarioSprite.__init__(self, x, y, SpriteType.BULLET_BILL)
        self.width = 4
        self.height = 12
        self.ya = -5
        self.facing = dir

    def clone(self):
        sprite = BulletBill(self.x, self.y, self.facing)
        sprite.xa = self.xa
        sprite.ya = self.ya
        sprite.width = self.width
        sprite.height = self.height
        return sprite

    def update(self):
        if not self.alive:
            return
        MarioSprite.update(self)
        sideWaysSpeed = 4
        self.xa = self.facing * sideWaysSpeed
        self._move(self.xa, 0)

    def collideCheck(self):
        if not self.alive:
            return

        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -16 and xMarioD < 16:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                if self.world.mario.ya > 0 and yMarioD <= 0 and (not self.world.mario.onGround or not self.world.mario.wasOnGround):
                    self.world.mario.stomp(self)
                    self.world.removeSprite(self)
                else:
                    self.world.addEvent(EventType.HURT, self.type.value)
                    self.world.mario.getHurt()

    def _move(self, xa, ya):
        self.x += xa
        return True

    def fireballCollideCheck(self, fireball):
        if not self.alive:
            return False
        xD = fireball.x - self.x
        yD = fireball.y - self.y
        if xD > -16 and xD < 16:
            return yD > -self.height and yD < fireball.height
        return False

    def shellCollideCheck(self, shell):
        if not self.alive:
            return False
        xD = shell.x - self.x
        yD = shell.y - self.y
        if xD > -16 and xD < 16:
            if yD > -self.height and yD < shell.height:
                self.world.addEvent(EventType.SHELL_KILL, self.type.value)
                self.world.removeSprite(self)
                return True
        return False
    
class FireFlower(MarioSprite):
    def __init__(self, x, y):
        MarioSprite.__init__(self, x, y, SpriteType.FIRE_FLOWER)
        self.width = 4
        self.height = 12
        self.facing = 1
        self._life = 0

    def clone(self):
        f = FireFlower(self.x, self.y)
        f.xa = self.xa
        f.ya = self.ya
        f.initialCode = self.initialCode
        f.width = self.width
        f.height = self.height
        f.facing = self.facing
        f._life = self._life
        return f

    def collideCheck(self):
        if not self.alive:
            return
        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -16 and xMarioD < 16:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                self.world.addEvent(EventType.COLLECT, self.type.value)
                self.world.mario.getFlower()
                self.world.removeSprite(self)

    def update(self):
        if not self.alive:
            return
        MarioSprite.update(self)
        self._life += 1
        if self._life < 9:
            self.y -= 1

class Fireball(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89

    def __init__(self, x, y, facing):
        MarioSprite.__init__(self, x, y, SpriteType.FIREBALL)
        self.facing = facing
        self.xa = 0
        self.ya = 4
        self.width = 4
        self.height = 8
        self.onGround = False

    def clone(self):
        f = Fireball(self.x, self.y, self.facing)
        f.xa = self.xa
        f.ya = self.ya
        f.initialCode = self.initialCode
        f.width = self.width
        f.height = self.height
        f.onGround = self.onGround
        return f

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True

        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.ya = 0
            if ya > 0:
                self.y = int(self.y / 16 + 1) * 16 - 1
                self.onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def _isBlocking(self, _x, _y, xa, ya):
        x = int(_x / 16)
        y = int(_y / 16)
        if x == int(self.x / 16) and y == int(self.y / 16):
            return False
        return self.world.level.isBlocking(x, y, xa, ya)

    def update(self):
        if not self.alive:
            return

        sideWaysSpeed = 8
        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1
        self.xa = self.facing * sideWaysSpeed
        self.world.checkFireballCollide(self)

        if not self._move(self.xa, 0):
            self.world.removeSprite(self)
            return

        self.onGround = False
        self._move(0, self.ya)
        if self.onGround:
            self.ya = -10
        self.ya *= 0.95
        if self.onGround:
            self.xa *= Fireball._GROUND_INERTIA
        else:
            self.xa *= Fireball._AIR_INERTIA

        if not self.onGround:
            self.ya += 1.5

class LifeMushroom(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89

    def __init__(self, x, y):
        MarioSprite.__init__(self, x, y, SpriteType.LIFE_MUSHROOM)
        self.width = 4
        self.height = 12
        self.facing = 1
        self.life = 0
        self.onGround = False

    def clone(self):
        m = LifeMushroom(self.x, self.y)
        m.xa = self.xa
        m.ya = self.ya
        m.initialCode = self.initialCode
        m.width = self.width
        m.height = self.height
        m.facing = self.facing
        m.life = self.life
        m.onGround = self.onGround
        return m

    def collideCheck(self):
        if not self.alive:
            return
        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -16 and xMarioD < 16:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                self.world.addEvent(EventType.COLLECT, self.type.value)
                self.world.mario.collect1Up()
                self.world.removeSprite(self)

    def _isBlocking(self, _x, _y, xa, ya):
        x = int(_x / 16)
        y = int(_y / 16)
        if x == int(self.x / 16) and y == int(self.y / 16):
            return False
        return self.world.level.isBlocking(x, y, xa, ya)

    def bumpCheck(self, xTile, yTile):
        if not self.alive:
            return
        if self.x + self.width > xTile * 16 and self.x - self.width < xTile * 16 + 16 and yTile == int((self.y - 1) / 16):
            self.facing = -self.world.mario.facing
            self.ya = -10

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True

        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.ya = 0
            if ya > 0:
                self.y = int(self.y / 16 + 1) * 16 - 1
                self.onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def update(self):
        if not self.alive:
            return
        if self.life < 9:
            self.y -= 1
            self.life += 1
            return
        sideWaysSpeed = 1.75
        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1
        self.xa = self.facing * sideWaysSpeed
        if not self._move(self.xa, 0):
            self.facing = -self.facing
        self.onGround = False
        self._move(0, self.ya)

        self.ya *= 0.85
        if self.onGround:
            self.xa *= LifeMushroom._GROUND_INERTIA
        else:
            self.xa *= LifeMushroom._AIR_INERTIA

        if not self.onGround:
            self.ya += 2

class Mushroom(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89

    def __init__(self, x, y):
        MarioSprite.__init__(self, x, y, SpriteType.MUSHROOM)
        self.width = 4
        self.height = 12
        self.facing = 1
        self.life = 0
        self.onGround = False
        self.life = 0

    def clone(self):
        m = Mushroom(self.x, self.y)
        m.xa = self.xa
        m.ya = self.ya
        m.initialCode = self.initialCode
        m.width = self.width
        m.height = self.height
        m.facing = self.facing
        m.life = self.life
        m.onGround = self.onGround
        return m

    def collideCheck(self):
        if not self.alive:
            return
        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -16 and xMarioD < 16:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                self.world.addEvent(EventType.COLLECT, self.type.value)
                self.world.mario.getMushroom()
                self.world.removeSprite(self)

    def _isBlocking(self, _x, _y, xa, ya):
        x = int(_x / 16)
        y = int(_y / 16)
        if x == int(self.x / 16) and y == int(self.y / 16):
            return False
        return self.world.level.isBlocking(x, y, xa, ya)

    def bumpCheck(self, xTile, yTile):
        if not self.alive:
            return
        if self.x + self.width > xTile * 16 and self.x - self.width < xTile * 16 + 16 and yTile == int((self.y - 1) / 16):
            self.facing = -self.world.mario.facing
            self.ya = -10

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self.isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True

        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.ya = 0
            if ya > 0:
                self.y = int(self.y / 16 + 1) * 16 - 1
                self.onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def update(self):
        if not self.alive:
            return
        if self.life < 9:
            self.y -= 1
            self.life += 1
            return
        sideWaysSpeed = 1.75
        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1
        self.xa = self.facing * sideWaysSpeed
        if not self._move(self.xa, 0):
            self.facing = -self.facing
        self.onGround = False
        self._move(0, self.ya)
        self.ya *= 0.85
        if self.onGround:
            self.xa *= Mushroom._GROUND_INERTIA
        else:
            self.xa *= Mushroom._AIR_INERTIA
        if not self.onGround:
            self.ya += 2

class Shell(MarioSprite):
    _GROUND_INERTIA = 0.89
    _AIR_INERTIA = 0.89

    def __init__(self, x, y, shellType, spriteCode):
        MarioSprite.__init__(self, x, y, SpriteType.SHELL)

        self.width = 4
        self.height = 12
        self.facing = 0
        self.ya = -5
        self.shellType = shellType
        self.initialCode = spriteCode
        self.onGround = False

    def clone(self):
        sprite = Shell(self.x, self.y, self.shellType, self.initialCode)
        sprite.xa = self.xa
        sprite.ya = self.ya
        sprite.width = self.width
        sprite.height = self.height
        sprite.facing = self.facing
        sprite.onGround = self.onGround
        return sprite

    def update(self):
        if not self.alive: 
            return
        MarioSprite.update(self)

        sideWaysSpeed = 11

        if self.xa > 2:
            self.facing = 1
        if self.xa < -2:
            self.facing = -1

        self.xa = self.facing * sideWaysSpeed

        if self.facing != 0:
            self.world.checkShellCollide(self)

        if not self._move(self.xa, 0):
            self.facing = -self.facing
        self.onGround = False
        self._move(0, self.ya)

        self.ya *= 0.85
        if self.onGround:
            self.xa *= Shell._GROUND_INERTIA
        else:
            self.xa *= Shell._AIR_INERTIA

        if not self.onGround:
            self.ya += 2

    def fireballCollideCheck(self, fireball):
        if not self.alive:
            return False

        xD = fireball.x - self.x
        yD = fireball.y - self.y

        if xD > -16 and xD < 16:
            if yD > -self.height and yD < fireball.height:
                if self.facing != 0:
                    return True
                self.xa = fireball.facing * 2
                self.ya = -5
                self.world.removeSprite(self)
                return True
        return False

    def collideCheck(self):
        if not self.alive:
            return

        xMarioD = self.world.mario.x - self.x
        yMarioD = self.world.mario.y - self.y
        if xMarioD > -16 and xMarioD < 16:
            if yMarioD > -self.height and yMarioD < self.world.mario.height:
                if self.world.mario.ya > 0 and yMarioD <= 0 and (not self.world.mario.onGround or not self.world.mario.wasOnGround):
                    self.world.mario.stomp(self)
                    if self.facing != 0:
                        self.xa = 0
                        self.facing = 0
                    else:
                        self.facing = self.world.mario.facing
                else:
                    if self.facing != 0:
                        self.world.addEvent(EventType.HURT, self.type.value)
                        self.world.mario.getHurt()
                    else:
                        self.world.addEvent(EventType.KICK, self.type.value)
                        self.world.mario.kick(self)
                        self.facing = self.world.mario.facing

    def _move(self, xa, ya):
        while xa > 8:
            if not self._move(8, 0):
                return False
            xa -= 8
        while xa < -8:
            if not self._move(-8, 0):
                return False
            xa += 8
        while ya > 8:
            if not self._move(0, 8):
                return False
            ya -= 8
        while ya < -8:
            if not self._move(0, -8):
                return False
            ya += 8

        collide = False
        if ya > 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya, xa, 0):
                collide = True
            elif self._isBlocking(self.x + xa - self.width, self.y + ya + 1, xa, ya):
                collide = True
            elif self._isBlocking(self.x + xa + self.width, self.y + ya + 1, xa, ya):
                collide = True
        if ya < 0:
            if self._isBlocking(self.x + xa, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            elif collide or self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
        if xa > 0:
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa + self.width, self.y + ya, xa, ya):
                collide = True
        if xa < 0:
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya - self.height / 2, xa, ya):
                collide = True
            if self._isBlocking(self.x + xa - self.width, self.y + ya, xa, ya):
                collide = True

        if collide:
            if xa < 0:
                self.x = int((self.x - self.width) / 16) * 16 + self.width
                self.xa = 0
            if xa > 0:
                self.x = int((self.x + self.width) / 16 + 1) * 16 - self.width - 1
                self.xa = 0
            if ya < 0:
                self.y = int((self.y - self.height) / 16) * 16 + self.height
                self.ya = 0
            if ya > 0:
                self.y = int(self.y / 16 + 1) * 16 - 1
                self.onGround = True
            return False
        else:
            self.x += xa
            self.y += ya
            return True

    def _isBlocking(self, _x, _y, xa, ya):
        x = int(_x / 16)
        y = int(_y / 16)
        if x == int(self.x / 16) and y == (int) (self.y / 16):
            return False
        blocking = self.world.level.isBlocking(x, y, xa, ya)
        if blocking and ya == 0 and xa != 0:
            self.world.bump(x, y, True)
        return blocking

    def bumpCheck(self, xTile, yTile):
        if not self.alive:
            return
        if self.x + self.width > xTile * 16 and self.x - self.width < xTile * 16 + 16 and yTile == int((self.y - 1) / 16):
            self.facing = -self.world.mario.facing
            self.ya = -10

    def shellCollideCheck(self, shell):
        if not self.alive:
            return
        xD = shell.x - self.x
        yD = shell.y - self.y

        if xD > -16 and xD < 16:
            if yD > -self.height and yD < shell.height:
                self.world.addEvent(EventType.SHELL_KILL, self.type.value)
                if self != shell:
                    self.world.removeSprite(shell)
                self.world.removeSprite(self)
                return True
        return False