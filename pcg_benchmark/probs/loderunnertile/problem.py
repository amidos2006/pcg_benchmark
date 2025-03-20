from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import DictionarySpace, ArraySpace, IntegerSpace
from pcg_benchmark.probs.loderunner.utils import play_loderunner, read_loderunner, js_dist
from pcg_benchmark.probs.utils import get_num_tiles, _get_certain_tiles, get_number_regions, get_vert_histogram, get_horz_histogram, get_range_reward
import numpy as np
import os
from PIL import Image

class LodeRunnerProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._gold = kwargs.get("gold")
        self._enemies = kwargs.get("enemies")

        self._target = kwargs.get("exploration",  0.2)
        self._islands = kwargs.get("islands", 0.1)
        self._decorations = kwargs.get("decorations", 0.75)
        self._used_tiles = kwargs.get("used_tiles", 0.75)
        self._diversity = kwargs.get("diversity", 0.4)
        
        self._walking = np.zeros(self._width)
        self._hanging = np.zeros(self._width)
        self._climbing = np.zeros(self._height + 1)
        self._falling = np.zeros(self._height + 1)
        lvls = [os.path.join(os.path.dirname(__file__) + "/data/", f) for f in os.listdir(os.path.dirname(__file__) + "/data/") if "level" in f]
        for lvl in lvls:
            exp = play_loderunner(read_loderunner(lvl))
            self._walking += get_horz_histogram(exp, [1])
            self._hanging += get_horz_histogram(exp, [3])
            self._climbing += get_vert_histogram(exp, [2])
            self._falling += get_vert_histogram(exp, [4])
        self._walking = np.array(self._walking) / sum(self._walking)
        self._hanging = np.array(self._hanging) / sum(self._hanging)
        self._climbing = np.array(self._climbing) / sum(self._climbing)
        self._falling = np.array(self._falling) / sum(self._falling)

        self._cerror = max(int(0.02 * self._width * self._height), 1)

        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(7))
        self._control_space = DictionarySpace({
            "ladder": IntegerSpace(int(0.2 * self._width * self._height)),
            "rope": IntegerSpace(int(0.2 * self._width * self._height))
        })

    def info(self, content):
        content = np.pad(np.array(content), ((0,1), (0,0)))

        empty = get_num_tiles(content, [1])
        player = get_num_tiles(content, [2])
        gold = get_num_tiles(content, [3])
        enemy = get_num_tiles(content, [4])
        ladder = get_num_tiles(content, [5])
        rope = get_num_tiles(content, [6])
        islands = 0
        for row in content:
            islands += get_number_regions(row.reshape(1,-1), [0])
            islands += get_number_regions(row.reshape(1,-1), [6])
        for col in content.transpose():
            islands += get_number_regions(col.reshape(1,-1), [5])

        collected_gold = 0
        tiles = 0
        used_tiles = 0
        exploration = np.zeros(content.shape)
        if player == 1:
            exploration = play_loderunner(content)
            for y in range(self._height):
                for x in range(self._width):
                    if content[y][x] == 0 and content[y-1][x] != 0 and y > 0:
                        tiles += 1
                        if exploration[y-1][x] > 0:
                            used_tiles += 1
                    if content[y][x] == 5 or content[y][x] == 6:
                        tiles += 1
                        if exploration[y][x] > 0:
                            used_tiles += 1
            locs = _get_certain_tiles(content, [3])
            for x,y in locs:
                if exploration[y][x] > 0:
                    collected_gold += 1
        
        walking = get_horz_histogram(exploration, [1])
        walking = np.array(walking) / max(1, sum(walking))
        hanging = get_horz_histogram(exploration, [3])
        hanging = np.array(hanging) / max(1, sum(hanging))
        climbing = get_vert_histogram(exploration, [2])
        climbing = np.array(climbing) / max(1, sum(climbing))
        falling = get_vert_histogram(exploration, [4]) 
        falling = np.array(falling) / max(1, sum(falling))

        return {
            "empty": empty,
            "player": player,
            "gold": gold,
            "enemy": enemy,
            "ladder": ladder,
            "rope": rope,
            "islands": islands,

            "exploration": exploration,
            "collected_gold": collected_gold,
            "used_tiles": used_tiles,
            "tiles": tiles,

            "walking": js_dist(walking, self._walking),
            "hanging": js_dist(hanging, self._hanging),
            "climbing": js_dist(climbing, self._climbing),
            "falling": js_dist(falling, self._falling)
        }
    
    def quality(self, info):
        stats = get_range_reward(info["player"], 0, 1, 1, self._width * self._height)
        stats += get_range_reward(info["gold"], 0, self._gold, 2 * self._gold, self._width * self._height)
        stats += get_range_reward(info["enemy"], 0, self._enemies, 2 * self._enemies, self._width * self._height)
        stats /= 3.0

        exploration = 0
        if stats >= 1:
            exploration += get_range_reward(((info["exploration"] > 0).astype(int)).sum(), 0,\
                int(self._target * self._width * self._height), self._width * self._height)
        
        play_stats = 0
        if exploration >= 1:
            play_stats += info["collected_gold"] / info["gold"]
            if info["tiles"] > 0:
                play_stats += get_range_reward(info["used_tiles"] / info["tiles"], 0, self._used_tiles, 1.0)
            play_stats /= 2.0

        decoration = 0
        if play_stats >= 1:
            decoration = 0.9 * (info["walking"] + info["hanging"] + info["climbing"]) + 0.1 * info["falling"]
            decoration = get_range_reward(decoration, 0, self._decorations, 1)
            decoration += get_range_reward(info["islands"], 0, 0, self._islands * self._width * self._height, self._width * self._height / 2)
            decoration /= 2

        return (stats + exploration + play_stats + decoration) / 4
    
    def diversity(self, info1, info2):
        walking = abs((info1["exploration"] == 1).astype(int) - (info2["exploration"] == 1).astype(int)).sum()
        stairs = abs((info1["exploration"] == 2).astype(int) - (info2["exploration"] == 2).astype(int)).sum()
        ropes = abs((info1["exploration"] == 3).astype(int) - (info2["exploration"] == 3).astype(int)).sum()
        falling = abs((info1["exploration"] == 4).astype(int) - (info2["exploration"] == 4).astype(int)).sum()
        return get_range_reward(0.3 * (walking + stairs + ropes) + 0.1 * falling, 0,\
            self._diversity * self._width * self._height, self._width * self._height)
    
    def controlability(self, info, control):
        ladder = get_range_reward(info["ladder"], 0, control["ladder"] - self._cerror, control["ladder"] + self._cerror, 
                                  self._width * self._height)
        rope = get_range_reward(info["rope"], 0, control["rope"] - self._cerror, control["rope"] + self._cerror, 
                                  self._width * self._height)
        return (ladder + rope) / 2
    
    def render(self, content):
        scale = 16
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/brick.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/player.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/gold.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/enemy.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/ladder.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/rope.png").convert('RGBA'),
        ]
        lvl = np.pad(np.array(content), ((0,1), (0,0)))
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                lvl_image.paste(graphics[lvl[y][x]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        return lvl_image