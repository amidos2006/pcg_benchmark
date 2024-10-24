from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import DictionarySpace, ArraySpace, IntegerSpace
from pcg_benchmark.probs.utils import get_number_regions, get_range_reward
from pcg_benchmark.probs.arcaderules.engine import runGame, getScript, Engine, DoNothingAgent, RandomAgent, FlatMCTSAgent
from PIL import Image, ImageDraw
import math
import numpy as np

"""
generate a fully connected map to test the rules against

Returns:
    int[][]: the fully connected layout of a level
"""
def _random_control(self):
    lvl = np.array(ArraySpace.sample(self))
    while(get_number_regions(lvl, [1]) != 1):
        lvl = np.array(ArraySpace.sample(self))
        symmetry = self._random.integers(2)
        quarters = [np.ones((int(lvl.shape[0] / 2), int(lvl.shape[1] / 2))).astype(int)]
        if symmetry > 0:
            quarters.append(np.ones((int(lvl.shape[0] / 2), int(lvl.shape[1] / 2))).astype(int))
        for q in quarters:
            number = self._random.integers(int(min(q.shape[0]/2, q.shape[1]/2))) + 2
            for _ in range(number):
                dir = self._random.integers(2)
                length = self._random.integers(max(q.shape[dir], 2)) + 1
                x = self._random.integers(max(int(q.shape[1]/2), 2))
                y = self._random.integers(max(int(q.shape[0]/2), 2))
                for i in range(length):
                    nx, ny = x + dir * i, y + (1-dir) * i
                    if nx > q.shape[1]-1 or ny > q.shape[0]-1:
                        break
                    q[ny][nx] = 0
        if len(quarters) == 1:
            newQuarter = quarters[0].copy()
            flip = self._random.integers(3)
            if flip:
                newQuarter = np.flip(newQuarter, axis=flip-1)
            quarters.append(newQuarter)
            
        flip = self._random.integers(2)
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

"""
Generate a 2D histogram of all the locations that has been visited by the objects

Parameters:
    objects(dict[str,any][]): the objects in the space. Each object should have "x" and "y"
    to be placed correctly in the histogram
    width(int): the size of the histogram map without padding
    height(int): the size of the histogram map without padding

Returns:
    int[][]: a 2D histogram for all the visited locations by the objects
"""
def _getMap(objects, width, height):
    layout = np.zeros((height, width))
    for obj in objects:
        if obj["alive"]:
            layout[obj["y"]-1][obj["x"]-1] += 1
    return layout

"""
Arcade Rules Problem based on the simple framework introduced by Togelius in 2008 in
An Experiment in Automatic Game Design. The goal is to generate new games and test them 
on a fixed layout or the one provided by the control parameter.
"""
class ArcadeRulesProblem(Problem):
    """
    constructor for the arcade rules problem

    Parameters:
        width(int): the width of the level that need to be tested against for the rule set
        height(int): the height of the level that need to be tested against for the rule set
        diversity(float): the diversity percentage that if passes it it is 1 (optional=0.4) 
        safety(float): the safety percentage that the do nothing agent need to not die until (optional=0.15) 
        minToDeath(float): the minimum percentage that random and agent need to lose in (optional=0.4)
        minToWin(float): the minimum percentage of steps needed for the flatmcts agent to take 
        before winning (optional=0.75) 
    """
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._diversity = kwargs.get("diversity", 0.25)
        self._s_target = kwargs.get("safety", 0.15)
        self._d_target = kwargs.get("minToDeath", 0.4)
        self._target = kwargs.get("minToWin", 0.75)
        self._render_type = "image"

        self._layout = np.ones((self._height, self._width))
        for x in range(math.ceil(0.25 * self._width), math.floor(self._width - 0.25 * self._width)):
            self._layout[math.floor(0.25 * self._height)][x] = 0
            self._layout[math.ceil(self._height - 0.25 * self._height - 1)][x] = 0
        for x in range(0, math.floor(0.3 * self._width)):
            self._layout[int(0.5 * self._height)][x] = 0
            self._layout[int(0.5 * self._height)][self._width - x - 1] = 0

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
                "score": IntegerSpace(4)
            })
        self._content_space = DictionarySpace(temp)
        self._control_space = ArraySpace((self._height, self._width), IntegerSpace(2))
        self._control_space.sample = _random_control.__get__(self._control_space, ArraySpace)
    
    """
    get stats and information about the content and return it

    Parameters:
        content(dict[str,any]): the content that needs to be tested

    Returns:
        dict[str,any]: information about the content that needs to test quality, diversity, controlability
        "player" x,y location - "red" x,y locations - "green" x,y locations - "yellow" x,y locations -
        "do_nothing" an array of state, action pairs for the do nothing agent - "random" an array of 
        state, action pairs for the random agent - "flat_mcts" an array of state, action pairs for the
        flatmcts agent - "max_time" the maximum time that the game can reach before ending
    """
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
    
    """
    Measure the quality of the content provided its information

    Parameters:
        into(dict[str,any]): the information of the content need to be measured for quality. Use info function
        to get the info for any content

    Returns:
        float: a value between 0 and 1 where 1 is passing the quality criteria
    """
    def quality(self, info):
        player = 0.0
        stats = 0.0
        if self._layout[info["player"]["y"]][info["player"]["x"]] == 1:
            player = 1.0
            canLose = int(info["do_nothing"][-1][0]['isLose'] or info["random"][-1][0]['isLose'] or info["flat_mcts"][-1][0]['isLose'])
            canWin = int(info["do_nothing"][-1][0]['isWin'] or info["random"][-1][0]['isWin'] or info["flat_mcts"][-1][0]['isWin'])
            survial = canWin
            if survial == 0:
                survial = get_range_reward(len(info["flat_mcts"]), 0, info["max_time"]+2)
            safety = get_range_reward(len(info["do_nothing"]), 0, self._s_target * info["max_time"], info["max_time"]+1)
            stats = (player + canLose + canWin + survial + safety) / 5.0
        death = 0.0
        if stats >= 1:
            donothing_death = get_range_reward(len(info["do_nothing"]), 0, self._s_target * info["max_time"],\
                info["max_time"]+1)
            random_death = get_range_reward(len(info["random"]), 0, 0, self._d_target * info["max_time"],\
                info["max_time"]+1)
            death = (donothing_death + random_death) / 2.0

        winValue = 0.0
        challenge = 0.0
        if death >= 1:
            winMCTS = int(info["flat_mcts"][-1][0]['isWin'])
            winRandom = int(info["random"][-1][0]['isWin'])
            winNothing = int(info["do_nothing"][-1][0]['isWin'])
            winValue = get_range_reward(2*winMCTS - winRandom - winNothing, -2, 2)
            challenge = get_range_reward(len(info["flat_mcts"]), 0, self._target * info["max_time"], info["max_time"]+1)
        
        return (stats + winValue + challenge + death) / 4.0
    
    """
    Measure the diversity between two contents using their infos

    Parameters:
        info1(dict[str,any]): the first content info
        info2(dict[str,any]): the second content info

    Returns:
        float: a value between 0 and 1 where 1 means these two content passed the criteria
    """
    def diversity(self, info1, info2):
        reds_1 = np.zeros((self._height, self._width))
        greens_1 = np.zeros((self._height, self._width))
        yellows_1 = np.zeros((self._height, self._width))
        for s,_ in info1["do_nothing"] + info1["random"] + info1["flat_mcts"]:
            reds_1 += _getMap(s['_reds'], self._width, self._height)
            greens_1 += _getMap(s['_greens'], self._width, self._height)
            yellows_1 += _getMap(s['_yellows'], self._width, self._height)
        player_1 = np.zeros((self._height, self._width))
        for s,_ in info1["flat_mcts"]:
            player_1[s['_player']["y"]-1][s['_player']["x"]-1] += 1
        
        reds_2 = np.zeros((self._height, self._width))
        greens_2 = np.zeros((self._height, self._width))
        yellows_2 = np.zeros((self._height, self._width))
        for s,_ in info2["do_nothing"] + info2["random"] + info2["flat_mcts"]:
            reds_2 += _getMap(s['_reds'], self._width, self._height)
            greens_2 += _getMap(s['_greens'], self._width, self._height)
            yellows_2 += _getMap(s['_yellows'], self._width, self._height)
        player_2 = np.zeros((self._height, self._width))
        for s,_ in info2["flat_mcts"]:
            player_2[s['_player']["y"]-1][s['_player']["x"]-1] += 1

        obj_div = abs((reds_1 > 0).astype(int) - (reds_2 > 0).astype(int)).sum() +\
            abs((greens_1 > 0).astype(int) - (greens_2 > 0).astype(int)).sum() +\
            abs((yellows_1 > 0).astype(int) - (yellows_2 > 0).astype(int)).sum()
        play_div = (abs(player_1 - player_2) > 0).sum()
        
        return get_range_reward((obj_div + play_div) / 2.0, 0, self._diversity * self._width * self._height, self._width, self._height)
    
    """
    Calculate the controlability on a content with respect to a control parameter

    Parameters:
        info(dict[str,any]): 
        control(int[][]):

    Returns:
        float: a value between 0 and 1 where 1 means that the content followed the control
    """
    def controlability(self, info, control):
        player = 0
        if control[info["player"]["y"]][info["player"]["x"]] == 1:
            player = 1.0
        value, total = 0, 0
        for key in ["red", "yellow", "green"]:
            for loc in info[key]:
                if control[loc["y"]][loc["x"]] == 1:
                    value += 1.0
                total += 1.0
        if total == 0:
            return 1.0
        return (value / total + player) / 2.0

    """
    Render the content and retrun it in form of PIL.Image. Since the content is rules, it is Image
    of written rules.

    Parameters:
        content(any): the content that needs to be rendered

    Returns:
        Image: the rules written in english language on an image and returned
    """
    def render(self, content):
        script = getScript(content)
        if self._render_type == "string":
            return script
        lines = script.split("\n")
        img = Image.new("RGBA", (300, 230), (71,45,60,255))
        draw = ImageDraw.Draw(img)
        x = 8
        y = 8
        draw.text((x,y), lines[0], fill=(60,172,215,255))
        y+=20
        draw.text((x,y), lines[1], fill=(207,198,184,255))
        y+= 12
        for key in ["red", "yellow", "green"]:
            locs = ""
            for i in range(content[f"{key}Start"]["num"]):
                locs += f"- {content[f'{key}Start']['x'][i]},{content[f'{key}Start']['y'][i]} "
        for i in range(3):
            draw.text((x,y), lines[i+2], fill=(191,121,88,255))
            y += 12
        y += 8
        draw.text((x,y), lines[5], fill=(207,198,184,255))
        y += 12
        for i in range(9):
            draw.text((x,y), lines[6+i], fill=(191,121,88,255))
            y += 12
        y += 8
        draw.text((x,y), lines[-1], fill=(244,180,27,255))
        return img