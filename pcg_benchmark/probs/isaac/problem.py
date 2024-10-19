from pcg_benchmark.probs import Problem
from pcg_benchmark.probs.utils import get_number_regions, get_num_tiles, get_range_reward, get_distance_length
from pcg_benchmark.spaces import DictionarySpace, ArraySpace, IntegerSpace
import os
import numpy as np
from PIL import Image

class IsaacProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")

        self._target = kwargs.get("map_size", 6)
        self._diversity = kwargs.get("diversity", 0.6)

        self._cerror = 0.2 * self._width * self._height

        self._content_space = DictionarySpace({
            "layout": ArraySpace((self._width * self._height), IntegerSpace(16)),
            "start": IntegerSpace(self._width * self._height),
            "boss": IntegerSpace(self._width * self._height),
            "shop": IntegerSpace(self._width * self._height),
            "treasure": IntegerSpace(self._width * self._height)
        })
        self._control_space = DictionarySpace({
            "map_size": IntegerSpace(self._target, self._width * self._height)
        })

    def info(self, content):
        layout = np.array(content["layout"]).reshape((self._height, self._width))
        map_size = get_num_tiles(layout, list(range(1, 16)))
        num_regions = get_number_regions(layout, list(range(1, 16)))
        
        maze_layout = np.zeros((3*self._height, 3*self._width)).astype(int)
        for y in range(self._height):
            for x in range(self._width):
                if layout[y][x] > 0:
                    maze_layout[3*y+1][3*x+1] = 1
                if layout[y][x] & 0x1:
                    maze_layout[3*y+1][3*x] = 2
                if layout[y][x] & 0x2:
                    maze_layout[3*y][3*x+1] = 2
                if layout[y][x] & 0x4:
                    maze_layout[3*y+1][3*x+2] = 2
                if layout[y][x] & 0x8:
                    maze_layout[3*y+2][3*x+1] = 2

        connect_regions = get_number_regions(maze_layout, [1,2])
        loose_connections = 0
        for y in range(maze_layout.shape[0]):
            for x in range(maze_layout.shape[1]):
                if x == 0 or x == maze_layout.shape[1] - 1 or y == 0 or y == maze_layout.shape[0] - 1:
                    if maze_layout[y][x] == 2:
                        loose_connections += 1
                    continue
                if (x - 1) % 3 == 1 and maze_layout[y][x] != maze_layout[y][x+1]:
                    loose_connections += 1
                    continue
                if (y - 1) % 3 == 1 and maze_layout[y][x] != maze_layout[y+1][x]:
                    loose_connections += 1
                    continue
        
        locations = set()
        if content["layout"][content["start"]] > 0:
            locations.add(content["start"])
        if content["layout"][content["boss"]] > 0:
            locations.add(content["boss"])
        if content["layout"][content["treasure"]] > 0:
            locations.add(content["treasure"])
        if content["layout"][content["shop"]] > 0:
            locations.add(content["shop"])
        
        player_x, player_y = content["start"] % self._width, int(content["start"] / self._width)
        boss_x, boss_y = content["boss"] % self._width, int(content["boss"] / self._width)
        level = maze_layout.copy()
        level[player_y][player_x] = 3
        level[boss_y][boss_x] = 4
        player_boss = get_distance_length(level, [3], [4], [1,2,3,4])

        dead_end = 0
        for v in [0x1, 0x2, 0x4, 0x8]:
            if content["layout"][content["boss"]] == v:
                dead_end += 1
            if content["layout"][content["treasure"]] == v:
                dead_end += 1
            if content["layout"][content["shop"]] == v:
                dead_end += 1

        return {
            "map_size": map_size,
            "num_regions": num_regions,
            "connect_regions": connect_regions,
            "loose_connections": loose_connections,
            "locations": len(locations),
            "player_boss_distance": player_boss,
            "flat": maze_layout.flatten(),
            "dead_end": dead_end
        }
    
    def quality(self, info):
        map_size = get_range_reward(info["map_size"], 0, self._target, self._width * self._height)
        regions = 0
        if map_size >= 1:
            regions += get_range_reward(info["num_regions"], 0, 1, 1, self._width * self._height)
            regions += get_range_reward(info["connect_regions"], 0, 1, 1, self._width * self._height)
        regions /= 2.0
        functional = 0
        if regions >= 1:
            functional += get_range_reward(info["locations"], 0, 4)
            functional += get_range_reward(info["player_boss_distance"], 0, self._width + self._height, 9 * self._width * self._height)
            functional /= 2.0
        loose_connections = 0
        if functional >= 1:
            loose_connections = get_range_reward(info["loose_connections"], 0, 0, 0, self._width * self._height)
        return 0.9 * (map_size + regions + functional) / 3 + 0.1 * loose_connections
    
    def diversity(self, info1, info2):
        hamming_rooms = (abs(info1["flat"] - info2["flat"]) == 1).sum()
        hamming_connections = (abs(info1["flat"] - info2["flat"]) == 2).sum()
        norm_rooms = get_range_reward(hamming_rooms, 0, self._width * self._height)
        norm_connections = get_range_reward(hamming_connections, 0, self._width * self._height)
        return get_range_reward(0.25 * norm_rooms + 0.75 * norm_connections, 0, self._diversity, 1)
    
    def controlability(self, info, control):
        map_size = get_range_reward(info["map_size"], control["map_size"]-self._cerror,\
            control["map_size"]+self._cerror, self._width * self._height)
        return map_size
    
    def render(self, content):
        scale = 16
        room_graphics = []
        for i in range(16):
            room_graphics.append(Image.open(os.path.dirname(__file__) + f"/images/room_{i+1}.png").convert('RGBA'))
        start = Image.open(os.path.dirname(__file__) + f"/images/start.png").convert('RGBA')
        boss = Image.open(os.path.dirname(__file__) + f"/images/boss.png").convert('RGBA')
        treasure = Image.open(os.path.dirname(__file__) + f"/images/treasure.png").convert('RGBA')
        shop = Image.open(os.path.dirname(__file__) + f"/images/shop.png").convert('RGBA')
        lvl_image = Image.new("RGBA", (self._width*scale, self._height*scale), (0,0,0,255))
        for y in range(self._height):
            for x in range(self._width):
                index = x + y * self._width
                lvl_image.paste(room_graphics[content["layout"][index]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        
        if content["layout"][content["shop"]] > 0:
            x = content["shop"] % self._width
            y = int(content["shop"] / self._width)
            lvl_image.paste(room_graphics[content["layout"][content["shop"]]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
            lvl_image.paste(shop, (x*scale, y*scale, (x+1)*scale, (y+1)*scale), shop)

        if content["layout"][content["treasure"]] > 0:
            x = content["treasure"] % self._width
            y = int(content["treasure"] / self._width)
            lvl_image.paste(room_graphics[content["layout"][content["treasure"]]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
            lvl_image.paste(treasure, (x*scale, y*scale, (x+1)*scale, (y+1)*scale), treasure)
        
        if content["layout"][content["boss"]] > 0:
            x = content["boss"] % self._width
            y = int(content["boss"] / self._width)
            lvl_image.paste(room_graphics[content["layout"][content["boss"]]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
            lvl_image.paste(boss, (x*scale, y*scale, (x+1)*scale, (y+1)*scale), boss)

        if content["layout"][content["start"]] > 0:
            x = content["start"] % self._width
            y = int(content["start"] / self._width)
            lvl_image.paste(room_graphics[content["layout"][content["start"]]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
            lvl_image.paste(start, (x*scale, y*scale, (x+1)*scale, (y+1)*scale), start)
        
        return lvl_image