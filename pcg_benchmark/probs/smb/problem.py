from pcg_benchmark.probs import Problem
from pcg_benchmark.probs.utils import get_range_reward, get_num_tiles
from pcg_benchmark.probs.smb.engine import runLevel
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, DictionarySpace
import numpy as np
import math
from PIL import Image
import os

def _convert2str(content, slices):
    content = np.pad(content, 3)
    width = len(content)
    height = len(slices[0])
    result = ""
    for y in range(height):
        for x in range(width):
            if x == 1 and y == height - 3:
                result += "M"
            elif x == width - 2 and y == height - 3:
                result += "F"
            else:
                result += slices[content[x]][y]
        result += '\n'
    return result

def _calculate_hnoise(content, slices):
    lvl = _convert2str(content, slices).split('\n')
    values = []
    for l in lvl:
        l = l.strip()
        if len(l) == 0:
            continue
        temp = 0
        for x in range(1,len(l)):
            if l[x] != l[x-1]:
                temp += 1
        temp /= (len(l) - 1)
        values.append(temp)
    return values

def _caculate_fenemies(content, slices):
    lvl = _convert2str(content, slices).split('\n')
    enemies = set('ykgr')
    solid = set('X#tSQ')
    total = 0
    floating = 0
    for x in range(len(lvl[0].strip())):
        for y in range(len(lvl)):
            lvl[y] = lvl[y].strip()
            if len(lvl[y]) == 0:
                continue
            if lvl[y][x] in enemies:
                total += 1
                if lvl[y+1][x] not in solid:
                    floating += 1
    if total == 0:
        return 0.0
    return floating/total

def _convert_action(action):
    result = 0
    for i in range(len(action)):
        result += int(action[i]) * pow(2, i)
    return result

class MarioProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._slices = []
        with open(os.path.dirname(__file__) + "/slices.txt") as f:
            strips = [l.strip() for l in f.readlines()]
            for s in strips:
                if len(s) > 0:
                    self._slices.append(s)
        self._hnoise = []
        with open(os.path.dirname(__file__) + "/noise.txt") as f:
            self._hnoise = np.array([float(v) for v in f.readlines()[0].strip().split(',')])
            
        self._width = kwargs.get("width")
        self._empty = kwargs.get("empty", 0.5)
        self._fenemies = kwargs.get("fenemies", 0.1)
        self._solver = kwargs.get("solver", 100 / (int(self._width < 30) + 1))
        self._timer = kwargs.get("timer", math.ceil(self._width / 10))
        self._diversity = kwargs.get("diversity", 0.4)

        self._content_space = ArraySpace((self._width,), IntegerSpace(len(self._slices)))
        self._control_space = DictionarySpace({"enemies": IntegerSpace(0, max(2, int(self._width / 7))), 
                                               "jumps": IntegerSpace(0, max(2, int(self._width / 5))), 
                                               "coins": IntegerSpace(0, max(2, int(self._width / 10)))})
        self._cerror = {"enemies": int(0.1 * self._control_space._value["enemies"]._max_value),
                        "jumps": int(0.1 * self._control_space._value["jumps"]._max_value),
                        "coins": int(0.1 * self._control_space._value["coins"]._max_value)}

    def parameters(self, **kwargs):
        Problem.parameters(self, **kwargs)

        self._diversity = kwargs.get("diversity", 0.4)
        self._solver = kwargs.get("solver", self._solver)
        self._timer = kwargs.get("timer", self._timer)

    def info(self, content):
        lvl = _convert2str(content, self._slices)
        lvl_lines = lvl.split("\n")
        tube_issue = 0
        for l in lvl_lines:
            test_tube = 0
            for c in l:
                if c == 't':
                    test_tube += 1
                else:
                    if test_tube % 2 > 0:
                        tube_issue += 1
                    test_tube = 0
        hnoise = np.array(_calculate_hnoise(content, self._slices)) - self._hnoise
        hnoise[hnoise < 0] = 0
        empty = get_num_tiles(np.array([content]), [0]) / len(content)
        fenemies = _caculate_fenemies(content, self._slices)
        
        if empty > self._empty and tube_issue == 0 and hnoise.sum() == 0 and fenemies < self._fenemies:
            result = runLevel(lvl, "heuristic", self._timer, self._solver)
            actions = []
            locations = []
            if result.getCompletionPercentage() >= 1.0:
                for ae in result.getAgentEvents():
                    actions.append(_convert_action(ae.getActions()))
                    locations.append([ae.getMarioX(), ae.getMarioY()])
            else:
                result = runLevel(lvl, "astar", self._timer, self._solver)
                for ae in result.getAgentEvents():
                    actions.append(_convert_action(ae.getActions()))
                    locations.append([ae.getMarioX(), ae.getMarioY()])
            
            return {
                "width": len(content),
                "tube": tube_issue,
                "empty": empty,
                "noise": hnoise,
                "fenemies": fenemies,
                "complete": result.getCompletionPercentage(),
                "enemies": max(0, result.getKillsTotal() - result.getKillsByFall()),
                "coins": result.getCurrentCoins(),
                "jumps": result.getNumJumps(),
                "actions": actions,
                "locations": locations,
            }
        else:
            return {
                "width": len(content),
                "tube": tube_issue,
                "noise": hnoise,
                "empty": empty,
                "fenemies": fenemies,
                "complete": 0.0,
                "enemies": 0.0,
                "coins": 0.0,
                "jumps": 0.0,
                "actions": [],
                "locations": []
            }

    def quality(self, info):
        tube = get_range_reward(info["tube"], 0, 0, 0, 10)
        empty = get_range_reward(info["empty"], 0, self._empty, 1)
        fenemeis = get_range_reward(info["fenemies"], 0, 0, self._fenemies, 1)
        noise = 0
        if empty >= 1 and tube >= 1:
            for n in info["noise"]:
                noise += get_range_reward(n, 0, 0, 0, 1)
        noise /= 16
        return (tube + empty + noise + fenemeis + 4 * info["complete"]) / 8.0

    def diversity(self, info1, info2):
        total = 0
        visited_1 = np.zeros((len(self._slices[0]), info1["width"]))
        for loc in info1["locations"]:
            x, y = max(0, min(15, int(loc[0] / 16))), max(0, min(15, int(loc[1] / 16)))
            visited_1[y][x] += 1
            total += 1
        visited_2 = np.zeros((len(self._slices[0]), info2["width"]))
        for loc in info2["locations"]:
            x, y = max(0, min(15, int(loc[0] / 16))), max(0, min(15, int(loc[1] / 16)))
            visited_2[y][x] += 1
            total += 1
        if total == 0:
            return 0.0
        return get_range_reward(abs(visited_1 - visited_2).sum() / total, 0, self._diversity, 1.0)
    
    def controlability(self, info, control):
        enemies = get_range_reward(info["enemies"], 0, max(0, control["enemies"] - self._cerror["enemies"]), control["enemies"] + self._cerror["enemies"], 100)
        jumps = get_range_reward(info["jumps"], 0, max(0, control["jumps"] - self._cerror["jumps"]), control["jumps"] + self._cerror["jumps"], 100)
        coins = get_range_reward(info["coins"], 0, max(0, control["coins"] - self._cerror["coins"]), control["coins"] + self._cerror["coins"], 100)
        return (enemies + jumps + coins) / 3.0
    
    def render(self, content):
        scale = 16
        graphics = {
            # empty locations
            "-": Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA'),

            # Flag
            "^": Image.open(os.path.dirname(__file__) + "/images/flag_top.png").convert('RGBA'),
            "f": Image.open(os.path.dirname(__file__) + "/images/flag_white.png").convert('RGBA'),
            "I": Image.open(os.path.dirname(__file__) + "/images/flag_middle.png").convert('RGBA'),

            # starting location
            "M": Image.open(os.path.dirname(__file__) + "/images/mario.png").convert('RGBA'),

            # Enemies
            "y": Image.open(os.path.dirname(__file__) + "/images/spiky.png").convert('RGBA'),
            "g": Image.open(os.path.dirname(__file__) + "/images/gomba.png").convert('RGBA'),
            "k": Image.open(os.path.dirname(__file__) + "/images/greenkoopa.png").convert('RGBA'),
            "r": Image.open(os.path.dirname(__file__) + "/images/redkoopa.png").convert('RGBA'),
            
            # solid tiles
            "X": Image.open(os.path.dirname(__file__) + "/images/floor.png").convert('RGBA'),
            "#": Image.open(os.path.dirname(__file__) + "/images/solid.png").convert('RGBA'),

            # Question Mark Blocks
            "Q": Image.open(os.path.dirname(__file__) + "/images/question_coin.png").convert('RGBA'),

            # Brick Blocks
            "S": Image.open(os.path.dirname(__file__) + "/images/brick.png").convert('RGBA'),

            # Coin
            "o": Image.open(os.path.dirname(__file__) + "/images/coin.png").convert('RGBA'),

            # Pipes
            "<": Image.open(os.path.dirname(__file__) + "/images/tubetop_left.png").convert('RGBA'),
            ">": Image.open(os.path.dirname(__file__) + "/images/tubetop_right.png").convert('RGBA'),
            "[": Image.open(os.path.dirname(__file__) + "/images/tube_left.png").convert('RGBA'),
            "]": Image.open(os.path.dirname(__file__) + "/images/tube_right.png").convert('RGBA'),
            "O": Image.open(os.path.dirname(__file__) + "/images/tubetop.png").convert('RGBA'),
            "H": Image.open(os.path.dirname(__file__) + "/images/tube.png").convert('RGBA'),
        }

        levelLines = _convert2str(content, self._slices).split('\n')
        width = len(levelLines[0])
        height = len(self._slices[0])

        decodedMap = []
        exit_x = -1
        exit_y = -1
        for y in range(height):
            decodedMap.append([])
            for x in range(width):
                char = levelLines[y][x]
                if char == "F":
                    exit_x = x
                    exit_y = y
                    char = "-"
                if char == "t":
                    singlePipe = True
                    topPipe = True
                    if(x < width - 1 and levelLines[y][x+1] == 't') or (x > 0 and levelLines[y][x-1] == 't'):
                        singlePipe = False
                    if y > 0 and levelLines[y-1][x] == 't':
                        topPipe = False
                    if singlePipe:
                        if topPipe:
                            char = "O"
                        else:
                            char = "H"
                    else:
                        if topPipe:
                            char = "<"
                            if x > 0 and levelLines[y][x-1] == 't':
                                char = ">"
                        else:
                            char = "["
                            if x > 0 and levelLines[y][x-1] == 't':
                                char = "]"
                decodedMap[y].append(char)

        if exit_x > 1:
            decodedMap[1][exit_x] = "^"
            decodedMap[2][exit_x - 1] = "f"
        for y in range(2,exit_y+1):
            decodedMap[y][exit_x] = "I"

        lvl_image = Image.new("RGBA", (width*scale, height*scale), (109,143,252,255))
        for y in range(height):
            for tx in range(width):
                x = width - tx - 1
                shift_x = 0
                if decodedMap[y][x] == "f":
                    shift_x = 8
                lvl_image.paste(graphics[decodedMap[y][x]], (x*scale + shift_x, y*scale, (x+1)*scale + shift_x, (y+1)*scale))
        return lvl_image
