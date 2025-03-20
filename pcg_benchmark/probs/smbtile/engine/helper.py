from enum import Enum

class EventType(Enum):
    BUMP = 1
    STOMP_KILL = 2
    FIRE_KILL = 3
    SHELL_KILL = 4
    FALL_KILL = 5
    JUMP = 6
    LAND = 7
    COLLECT = 8
    HURT = 9
    KICK = 10
    LOSE = 11
    WIN = 12

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other

class GameStatus(Enum):
    RUNNING = 0
    WIN = 1
    LOSE = 2
    TIME_OUT = 3

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other

class MarioActions(Enum):
    LEFT = 0
    RIGHT = 1
    DOWN = 2
    SPEED = 3
    JUMP = 4

    def numberOfActions():
        return len(MarioActions)

    def getAction(value):
        return MarioActions(value)
    
    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other
    
class SpriteType(Enum):
    # Generic values
    NONE = 0,
    UNDEF = -42
    MARIO = -31
    FIREBALL = 16
    GOOMBA = 2
    GOOMBA_WINGED = 3
    RED_KOOPA = 4
    RED_KOOPA_WINGED = 5
    GREEN_KOOPA = 6
    GREEN_KOOPA_WINGED = 7
    SPIKY = 8
    SPIKY_WINGED = 9
    BULLET_BILL = 10
    ENEMY_FLOWER = 11
    MUSHROOM = 12
    FIRE_FLOWER = 13
    SHELL = 14
    LIFE_MUSHROOM = 15

    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other

class TileFeature(Enum):
    BLOCK_UPPER = 0
    BLOCK_ALL = 1
    BLOCK_LOWER = 2
    SPECIAL = 3
    LIFE = 4
    BUMPABLE = 5
    BREAKABLE = 6
    PICKABLE = 7
    ANIMATED = 8
    SPAWNER = 9

    def getTileType(index):
        features = []
        if index == 1 or index == 2 or index == 14 or index == 18 or index == 19 or\
            index == 20 or index == 21 or index == 4 or index == 5 or index == 52 or\
            index == 53:
            features.append(TileFeature.BLOCK_ALL)
        elif index == 43 or index == 44 or index == 45 or index == 46:
            features.append(TileFeature.BLOCK_LOWER)
        elif index == 48:
            features.append(TileFeature.BLOCK_UPPER)
            features.append(TileFeature.LIFE)
            features.append(TileFeature.BUMPABLE)
        elif index == 49:
            features.append(TileFeature.BUMPABLE)
            features.append(TileFeature.BLOCK_UPPER)
        elif index == 3:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.SPAWNER)
        elif index == 8:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.SPECIAL)
            features.append(TileFeature.BUMPABLE)
            features.append(TileFeature.ANIMATED)    
        elif index == 11:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.BUMPABLE)
            features.append(TileFeature.ANIMATED)
        elif index == 6:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.BREAKABLE)
        elif index == 7:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.BUMPABLE)
        elif index == 15:
            features.append(TileFeature.PICKABLE)
            features.append(TileFeature.ANIMATED) 
        elif index == 50:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.SPECIAL)
            features.append(TileFeature.BUMPABLE)
        elif index == 51:
            features.append(TileFeature.BLOCK_ALL)
            features.append(TileFeature.LIFE)
            features.append(TileFeature.BUMPABLE)
        return features
    
    def __eq__(self, other):
        if hasattr(other, "value"):
            return self.value == other.value
        return self.value == other