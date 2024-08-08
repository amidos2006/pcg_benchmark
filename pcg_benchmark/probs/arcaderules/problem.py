from pcg_benchmark.probs.problem import Problem
from pcg_benchmark.spaces import DictionarySpace, ArraySpace, IntegerSpace
from pcg_benchmark.probs.utils import get_number_regions, get_range_reward
from pcg_benchmark.probs.arcaderules.engine import runGame, Engine, DoNothingAgent, RandomAgent, FlatMCTSAgent
from PIL import Image, ImageDraw
import math
import numpy as np

def _getMap(objects, width, height):
    layout = np.zeros((height+2, width+2))
    for obj in objects:
        if obj["alive"]:
            layout[obj["y"]][obj["x"]] += 1
    return layout

class ArcadeRulesProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")

        self._layout = np.ones((self._height, self._width))
        for x in range(math.ceil(0.25 * self._width), math.floor(self._width - 0.25 * self._width)):
            self._layout[math.floor(0.25 * self._height)][x] = 0
            self._layout[math.ceil(self._height - 0.25 * self._height - 1)][x] = 0
        for x in range(0, math.floor(0.3 * self._width)):
            self._layout[int(0.5 * self._height)][x] = 0
            self._layout[int(0.5 * self._height)][self._width - x - 1] = 0
        
        self._diversity = kwargs.get("diversity", 0.25)
        self._s_target = kwargs.get("safety", 5)
        self._d_target = kwargs.get("minToDeath", 15)
        self._target = kwargs.get("minToWin", 30)

        temp = {
            "x": IntegerSpace(self._width),
            "y": IntegerSpace(self._height),
            "seed": IntegerSpace(pow(10, 6)),
            "win": IntegerSpace(4)
        }
        for key in ["red", "yellow", "green"]:
            temp[key] = IntegerSpace(8)
            temp[f"{key}Start"] = DictionarySpace({
                "num": IntegerSpace(5),
                "x": ArraySpace((4), IntegerSpace(self._width)),
                "y": ArraySpace((4), IntegerSpace(self._height))
            })

        for key in ["player-red", "player-green", "player-yellow", "red-red", "red-green",\
                    "red-yellow", "green-green", "green-yellow", "yellow-yellow"]:
            temp[key] = DictionarySpace({
                "action": IntegerSpace(4),
                "score": IntegerSpace(3)
            })
        self._content_space = DictionarySpace(temp)
        self._control_space = ArraySpace((self._height, self._width), IntegerSpace(2))

    def random_control(self):
        lvl = np.array(super().random_control())
        while(get_number_regions(lvl, [1]) != 1):
            lvl = np.array(super().random_control())
            symmetry = np.random.randint(2)
            quarters = [np.ones((int(self._height / 2), int(self._width / 2))).astype(int)]
            if symmetry > 0:
                quarters.append(np.ones((int(self._height / 2), int(self._width / 2))).astype(int))
            for q in quarters:
                number = np.random.randint(int(min(q.shape[0]/2, q.shape[1]/2))) + 2
                for _ in range(number):
                    dir = np.random.randint(2)
                    length = np.random.randint(max(q.shape[dir], 2)) + 1
                    x = np.random.randint(max(int(q.shape[1]/2), 2))
                    y = np.random.randint(max(int(q.shape[0]/2), 2))
                    for i in range(length):
                        nx, ny = x + dir * i, y + (1-dir) * i
                        if nx > q.shape[1]-1 or ny > q.shape[0]-1:
                            break
                        q[ny][nx] = 0
            if len(quarters) == 1:
                newQuarter = quarters[0].copy()
                flip = np.random.randint(3)
                if flip:
                    newQuarter = np.flip(newQuarter, axis=flip-1)
                quarters.append(newQuarter)
                
            flip = np.random.randint(2)
            for y in range(quarters[0].shape[0]):
                for x in range(quarters[0].shape[1]):
                    lvl[y][x] = quarters[0][y][x]
                    if flip:
                        lvl[lvl.shape[0]-1-y][lvl.shape[1]-1-x] = quarters[0][y][x]
                    else:
                        lvl[y][lvl.shape[1]-1-x] = quarters[0][y][x]
                    lvl[lvl.shape[0]-1-y][x] = quarters[1][y][x]
                    if flip:
                        lvl[y][lvl.shape[1]-1-x] = quarters[1][y][x]
                    else:
                        lvl[lvl.shape[0]-1-y][lvl.shape[1]-1-x] = quarters[1][y][x]
        return lvl
    
    def info(self, content):
        player = 0
        if self._layout[content["y"]][content["x"]] == 1:
            player = 1.0
        red, green, yellow = [], [], []
        for i in range(content["redStart"]["num"]):
            red.append({"x": content["redStart"]["x"][i], "y": content["redStart"]["y"][i]})
        for i in range(content["greenStart"]["num"]):
            green.append({"x": content["greenStart"]["x"][i], "y": content["greenStart"]["y"][i]})
        for i in range(content["yellowStart"]["num"]):
            yellow.append({"x": content["yellowStart"]["x"][i], "y": content["yellowStart"]["y"][i]})
        doNothing = []
        random = []
        flatMCTS = []
        maxTime = 0
        if player > 0:
            engine = Engine(content, self._layout)
            doNothing = runGame(engine, DoNothingAgent())
            random = runGame(engine, RandomAgent(content["seed"]))
            flatMCTS = runGame(engine, FlatMCTSAgent(content["seed"]))
            maxTime = engine._maxTime
        return {
            "player": {"x": content["x"], "y": content["y"]},
            "red": red,
            "green": green,
            "yellow": yellow,
            "do_nothing": doNothing,
            "random": random,
            "flat_mcts": flatMCTS,
            "max_time": maxTime
        }
    
    def quality(self, info):
        player = 0.0
        stats = 0.0
        if self._layout[info["player"]["y"]][info["player"]["x"]] == 1:
            player = 1.0
            canLose = int(info["do_nothing"][-1][0].isLose() or info["random"][-1][0].isLose() or info["flat_mcts"][-1][0].isLose())
            canWin = int(info["do_nothing"][-1][0].isWin() or info["random"][-1][0].isWin() or info["flat_mcts"][-1][0].isWin())
            safety = get_range_reward(len(info["do_nothing"]), 0, self._s_target, info["max_time"])
            stats = (player + canLose + canWin + safety) / 4.0
        
        death = 0.0
        if stats >= 1:
            donothing_death = get_range_reward(len(info["do_nothing"]), 0, self._s_target, self._d_target, info["max_time"])
            random_death = get_range_reward(len(info["random"]), 0, 0, self._d_target, info["max_time"])
            death = (donothing_death + random_death) / 2.0

        winValue = 0.0
        challenge = 0.0
        if death >= 1:
            winMCTS = int(info["flat_mcts"][-1][0].isWin())
            winRandom = int(info["random"][-1][0].isWin())
            winNothing = int(info["do_nothing"][-1][0].isWin())
            winValue = get_range_reward(winMCTS - winRandom - winNothing, -2, 2)
            challenge = get_range_reward(len(info["flat_mcts"]), 0, self._target, info["max_time"])
        
        return (stats + winValue + challenge + death) / 4.0
    
    def diversity(self, info1, info2):
        reds_1 = np.zeros((self._height+2, self._height+2))
        greens_1 = np.zeros((self._height+2, self._height+2))
        yellows_1 = np.zeros((self._height+2, self._height+2))
        for s,_ in info1["do_nothing"] + info1["random"] + info1["flat_mcts"]:
            reds_1 += _getMap(s._reds, self._width, self._height)
            greens_1 += _getMap(s._greens, self._width, self._height)
            yellows_1 += _getMap(s._yellows, self._width, self._height)
        player_1 = np.zeros((self._height+2, self._height+2))
        for s,_ in info1["flat_mcts"]:
            player_1[s._player["y"]][s._player["x"]] += 1
        
        reds_2 = np.zeros((self._height+2, self._height+2))
        greens_2 = np.zeros((self._height+2, self._height+2))
        yellows_2 = np.zeros((self._height+2, self._height+2))
        for s,_ in info2["do_nothing"] + info2["random"] + info2["flat_mcts"]:
            reds_2 += _getMap(s._reds, self._width, self._height)
            greens_2 += _getMap(s._greens, self._width, self._height)
            yellows_2 += _getMap(s._yellows, self._width, self._height)
        player_2 = np.zeros((self._height+2, self._height+2))
        for s,_ in info2["flat_mcts"]:
            player_2[s._player["y"]][s._player["x"]] += 1

        obj_div = abs((reds_1 > 0).astype(int) - (reds_2 > 0).astype(int)).sum() +\
            abs((greens_1 > 0).astype(int) - (greens_2 > 0).astype(int)).sum() +\
            abs((yellows_1 > 0).astype(int) - (yellows_2 > 0).astype(int)).sum()
        play_div = (abs(player_1 - player_2) > 0).sum()
        
        return get_range_reward((obj_div + play_div) / 2.0, 0, self._diversity * self._width * self._height, self._width, self._height)
    
    def controlability(self, info, control):
        player = 0
        if control[info["player"]["y"]][info["player"]["x"]] == 1:
            player = 1.0
        value, total = 0, 0
        for key in ["red", "yellow", "green"]:
            for loc in range(len(info[key])):
                if control[loc["y"]][loc["x"]] == 1:
                    value += 1.0
                total += 1.0
        if total == 0:
            return 1.0
        return (value / total + player) / 2.0

    def render(self, content):
        behaviors = ["still", "flicker", "randomShort", "randomLong", "wanderHorz", "wanderVert", "chase", "flee"]
        win = ["time", "score5", "score10", "score20"]
        action = ["none", "killFirst", "killSecond", "killBoth"]

        img = Image.new("RGBA", (300, 230), (71,45,60,255))
        draw = ImageDraw.Draw(img)
        x = 8
        y = 8
        draw.text((x,y), f"Start: {content['x']},{content['y']} - {content['seed']}", fill=(60,172,215,255))
        y+=20
        draw.text((x,y), "Behavior:", fill=(207,198,184,255))
        y+= 12
        x = 16
        for key in ["red", "yellow", "green"]:
            locs = ""
            for i in range(content[f"{key}Start"]["num"]):
                locs += f"- {content[f'{key}Start']['x'][i]},{content[f'{key}Start']['y'][i]} "
            draw.text((x,y), f"{key}: {behaviors[content[key]]} {locs}", fill=(191,121,88,255))
            y += 12
        y += 8
        x = 8
        draw.text((x,y), "Rules:", fill=(207,198,184,255))
        y += 12
        x = 16
        for key in ["player-red", "player-green", "player-yellow", "red-red", "red-green",\
                    "red-yellow", "green-green", "green-yellow", "yellow-yellow"]:
            draw.text((x,y), f"{key}: {action[content[key]['action']]} - {content[key]['score']}", fill=(191,121,88,255))
            y += 12
        y += 8
        x = 8
        draw.text((x,y), f"Win: {win[content['win']]}", fill=(244,180,27,255))
        return img