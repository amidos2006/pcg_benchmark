from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, DictionarySpace
from pcg_benchmark.probs.utils import get_number_regions, get_range_reward, get_num_tiles, get_distance_length, get_path
from difflib import SequenceMatcher
import numpy as np
from PIL import Image
import os

from enum import IntEnum

class Tile(IntEnum):
    WALL = 0,
    EMPTY = 1,
    PLAYER = 2,
    KEY = 3,
    DOOR = 4,
    ENEMY = 5


class ZeldaProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)
        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._enemies = kwargs.get("enemies")
        self._diversity = kwargs.get("diversity", 0.3)
        self._erange = max(int(self._enemies * 0.25), 1)

        self._target = kwargs.get("sol_length", self._width + self._height)
        self._cerror = max(int(self._target / 2 * 0.25), 1)

        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(6))
        self._control_space = DictionarySpace({
            "player_key": IntegerSpace(int(self._target / 2 + self._cerror), int(self._width * self._height / 4)),
            "key_door": IntegerSpace(int(self._target / 2 + self._cerror), int(self._width * self._height / 4))
        })
        # the quality compute is using the self._target, and the self._control_space is seperately sampling the 2 paths
        # just note that if the target is using the default value and control is using the sample from the control space, their values might be different

    def info(self, content):
        content = np.array(content)
        number_regions = get_number_regions(content, [Tile.EMPTY, Tile.PLAYER, Tile.KEY, Tile.DOOR, Tile.ENEMY])
        number_player = get_num_tiles(content, [Tile.PLAYER])
        number_key = get_num_tiles(content, [Tile.KEY])
        number_door = get_num_tiles(content, [Tile.DOOR])
        number_enemies = get_num_tiles(content, [Tile.ENEMY])
        player_key = get_distance_length(content, [Tile.PLAYER], [Tile.KEY], [Tile.EMPTY, Tile.PLAYER, Tile.KEY, Tile.ENEMY])
        pk_path = get_path(content, [Tile.PLAYER], [Tile.KEY], [Tile.EMPTY, Tile.PLAYER, Tile.KEY, Tile.ENEMY])
        key_door = get_distance_length(content, [Tile.KEY], [Tile.DOOR], [Tile.EMPTY, Tile.PLAYER, Tile.KEY, Tile.DOOR, Tile.ENEMY])
        kd_path = get_path(content, [Tile.KEY], [Tile.DOOR], [Tile.EMPTY, Tile.PLAYER, Tile.KEY, Tile.DOOR, Tile.ENEMY]) # the target need to be set as pass
        
        return {
            "regions": number_regions, "players": number_player, 
            "keys": number_key, "doors": number_door, "enemies": number_enemies,
            "player_key": player_key, "key_door": key_door,
            "pk_path": pk_path, "kd_path": kd_path,
        }

    def quality(self, info):
        regions = get_range_reward(info["regions"], 0, 1, 1, self._width * self._height / 10)

        player = get_range_reward(info["players"], 0, 1, 1, self._width * self._height)
        key = get_range_reward(info["keys"], 0, 1, 1, self._width * self._height)
        door = get_range_reward(info["doors"], 0, 1, 1, self._width * self._height)
        enemies = get_range_reward(info["enemies"], 0, self._enemies - self._erange, \
                                   self._enemies + self._erange, self._width * self._height)
        stats = (player + key + door + enemies) / 4.0

        added = 0
        if player >= 1 and key >= 1 and door >= 1:
            playable = 0
            if info["player_key"] > 0:
                playable += 1.0
            if info["key_door"] > 0:
                playable += 1.0
            playable /= 2.0
            added += playable
            if playable == 1:
                sol_length = get_range_reward(info["player_key"] + info["key_door"], 0, self._target,\
                                       self._width * self._height)
                added += sol_length
        return (regions + stats + added) / 4.0

    def diversity(self, info1, info2):
        path1 = info1["pk_path"] + info1["kd_path"]
        new_path1 = ""
        for x,y in path1:
            if path1[0][0] > self._width / 2:
                x = self._width - x - 1
            if path1[0][1] > self._height / 2:
                y = self._height - y - 1
            new_path1 += f"{x},{y}|"

        path2 = info2["pk_path"] + info2["kd_path"]
        new_path2 = ""
        for x,y in path2:
            if path2[0][0] > self._width / 2:
                x = self._width - x - 1
            if path2[0][1] > self._height / 2:
                y = self._height - y - 1
            new_path2 += f"{x},{y}|"
        ratio = SequenceMatcher(None, new_path1, new_path2).ratio()
        return get_range_reward(1 - ratio, 0, self._diversity, 1.0)
    
    def controlability(self, info, control):
        player_key = get_range_reward(info["player_key"], 0, control["player_key"]-self._cerror, control["player_key"]+self._cerror, int(self._width * self._height / 4))
        key_door = get_range_reward(info["key_door"], 0, control["key_door"]-self._cerror, control["key_door"]+self._cerror, int(self._width * self._height / 4))
        return (player_key + key_door) / 2
    
    def render(self, content):
        scale = 16
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/solid.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/player.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/key.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/door.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/bat.png").convert('RGBA'),
        ]
        lvl = np.pad(np.array(content), 1)
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                lvl_image.paste(graphics[lvl[y][x]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        return lvl_image