from pcg_benchmark.probs import Problem
from pcg_benchmark.probs.ddave.engine import State,BFSAgent,AStarAgent
from pcg_benchmark.probs.utils import get_num_tiles, get_regions_size, _flood_fill, _get_certain_tiles, get_range_reward
from pcg_benchmark.spaces import ArraySpace, DictionarySpace, IntegerSpace
import numpy as np
from PIL import Image
import os

def _getLvl(content):
    content = np.array(content)
    player_locations = _get_certain_tiles(content, [2])
    if len(player_locations) > 0:
        regions = get_regions_size(content, player_locations, [1,2,3,4,5,6])
        loc = player_locations[np.argmax(regions)]
        color_map = np.full(content.shape, -1)
        _flood_fill(loc[0], loc[1], color_map, content, 1, [1,2,3,4,5,6])
        color_map[color_map == -1] = 0
        content = content * color_map
    return content

def _run_game(content, solver_power, target = None):
    lvl = np.pad(content, 1)
    gameCharacters="# @H$V*"
    lvlString = ""
    for i in range(lvl.shape[0]):
        for j in range(lvl.shape[1]):
            lvlString += gameCharacters[int(lvl[i][j])]
            if j == lvl.shape[1]-1:
                lvlString += "\n"
    state = State()
    state.stringInitialize(lvlString.split("\n"))
    state.target = target
    
    aStarAgent = AStarAgent()
    bfsAgent = BFSAgent()

    sol,solState,_ = aStarAgent.getSolution(state, 1, solver_power)
    if solState.checkWin():
        return 0, sol, solState.getGameStatus()
    sol,solState,_ = aStarAgent.getSolution(state, 0.5, solver_power)
    if solState.checkWin():
        return 0, sol, solState.getGameStatus()
    sol,solState,_ = aStarAgent.getSolution(state, 0, solver_power)
    if solState.checkWin():
        return 0, sol, solState.getGameStatus()
    sol,solState,_ = bfsAgent.getSolution(state, solver_power)
    if solState.checkWin():
        return 0, sol, solState.getGameStatus()

    return solState.getHeuristic(), [], solState.getGameStatus()

class DangerDaveProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._jumps = kwargs.get("jumps")
        self._solver = kwargs.get("solver", 5000)
        self._diversity = kwargs.get("diversity", 0.4)

        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(7))
        self._control_space = DictionarySpace({
            "sx": IntegerSpace(self._width), 
            "sy": IntegerSpace(int(self._height / 2) + 2, self._height),
            "ex": IntegerSpace(self._width),
            "ey": IntegerSpace(int(self._height/2)),
            "diamonds": IntegerSpace(0, min(self._width, self._height))
        })

    def info(self, content):
        content = _getLvl(content)
        player_locations = _get_certain_tiles(content, [2])
        players = len(player_locations)
        exit_locations = _get_certain_tiles(content, [3])
        exits = len(exit_locations)
        keys = get_num_tiles(content, [5])
        spikes = get_num_tiles(content, [6])
        diamonds = _get_certain_tiles(content, [4])
        heuristic, solution, stats, diamondHeuristic = -1, [], {}, []
        playerOnGround = 0
        for loc in player_locations:
            playerOnGround += int(loc[1] == self._height - 1 or content[loc[1] + 1][loc[0]] == 0)
        exitOnGround = 0
        for loc in exit_locations:
            exitOnGround += int(loc[1] == self._height - 1 or content[loc[1] + 1][loc[0]] == 0)
        if players == 1 and exits == 1 and keys == 1:
            heuristic, solution, stats = _run_game(content, self._solver)
            for d in diamonds:
                dh, _, _ = _run_game(content, self._solver, {"x": d[0]+1, "y": d[1]+1})
                diamondHeuristic.append(dh)
            for a in solution:
                a["x"], a["y"] = a["x"] - 1, a["y"] - 1
        result =  {
            "players": players, "exits": exits, "diamonds": len(diamonds), "keys": keys, "spikes": spikes,
            "playerOnGround": playerOnGround, "player_locations": player_locations, "exit_locations": exit_locations,
            "exitOnGround": exitOnGround, "diamond_reachable": diamondHeuristic, "heuristic": heuristic, "solution": solution,
            "repaired_content": content
        }
        for name in stats:
            result[name] = stats[name]
        return result
    
    def quality(self, info):
        player = get_range_reward(info["players"], 0, 1, 1, self._width * self._height)
        playerExitOnGround = get_range_reward(info["playerOnGround"] + info["exitOnGround"], 0, info["players"] + info["exits"], self._width * self._height)
        exit = get_range_reward(info["exits"], 0, 1, 1, self._width * self._height)
        key = get_range_reward(info["keys"], 0, 1, 1, self._width * self._height)
        spikes = get_range_reward(info["spikes"], 0, 0, 2 * max(self._width, self._height), self._width * self._height)
        stats = (player + playerExitOnGround + exit + key + spikes) / 5.0
        play_stats = 0
        diamond_stats = 0
        if player == 1 and exit == 1 and key == 1:
            play_stats += get_range_reward(info["heuristic"],0,0,0, self._width * self._height)
            play_stats += get_range_reward(info["num_jumps"],0,self._jumps, max(self._width,self._height))
            play_stats = play_stats / 2.0
            for dh in info["diamond_reachable"]:
                diamond_stats += get_range_reward(dh,0,0,0,self._width * self._height)
            if info["diamonds"] == 0:
                diamond_stats = 1.0
            else:
                diamond_stats /= info["diamonds"]
            diamond_stats += get_range_reward(info["diamonds"], 0, 0, min(self._width, self._height), self._width * self._height)
            diamond_stats /= 2.0
        return (stats + play_stats + diamond_stats) / 3.0
    
    def diversity(self, info1, info2):
        path1 = np.zeros((self._height, self._width))
        min_x, min_y = 0, 0
        if len(info1["solution"] + info2["solution"]) > 0:
            min_x, min_y = min([a["x"] for a in info1["solution"] + info2["solution"]]), min([a["y"] for a in info1["solution"] + info2["solution"]])
        for a in info1["solution"]:
            path1[a["y"]-min_y][a["x"]-min_x] += 1
        path2 = np.zeros((self._height, self._width))
        for a in info2["solution"]:
            path2[a["y"]-min_y][a["x"]-min_x] += 1
        path1_f = np.flip(path1, axis=1)
        diff = min(abs(path1 - path2).sum(), abs(path1_f - path2).sum())
        return get_range_reward(diff, 0, self._diversity * (self._width + self._height), self._width * self._height)
    
    def controlability(self, info, control):
        start_error = self._width * self._height
        for loc in info["player_locations"]:
            dist = abs(control["sx"] - loc[0]) + abs(control["sy"] - loc[1])
            if dist < start_error:
                start_error = dist
        exit_error = self._width * self._height
        for loc in info["exit_locations"]:
            dist = abs(control["ex"] - loc[0]) + abs(control["ey"] - loc[1])
            if dist < exit_error:
                exit_error = dist
        diamond_error = abs(control["diamonds"] - info["diamonds"])
        return (get_range_reward(start_error, 0, 0, 0, self._width + self._height) +\
                get_range_reward(exit_error, 0, 0, 0, self._width + self._height)+\
                get_range_reward(diamond_error, 0, 0, 0, self._width * self._height)) / 3.0

    def render(self, content):
        scale = 16
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/solid.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/player.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/exit.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/diamond.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/key.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/spike.png").convert('RGBA'),
        ]
        lvl = np.pad(_getLvl(content), 1)
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                lvl_image.paste(graphics[lvl[y][x]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        return lvl_image