from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import ArraySpace, DictionarySpace, IntegerSpace
from pcg_benchmark.probs.utils import get_number_regions, get_num_tiles, _get_certain_tiles, get_range_reward
from pcg_benchmark.probs.mdungeons.engine import State,BFSAgent,AStarAgent
import numpy as np
from PIL import Image
from difflib import SequenceMatcher
import os

def _get_solution_sequence(content, sol):
    lvl = np.pad(content, 1)
    gameCharacters="# @H*$go"
    lvlString = ""
    for i in range(lvl.shape[0]):
        for j in range(lvl.shape[1]):
            lvlString += gameCharacters[int(lvl[i][j])]
            if j == lvl.shape[1]-1:
                lvlString += "\n"
    state = State()
    state.stringInitialize(lvlString.split("\n"))

    result = ""
    for a in sol:
        result += state.update(a["action"]["x"], a["action"]["y"])
    return result

def _run_game(content, solver_power):
    lvl = np.pad(content, 1)
    gameCharacters="# @H*$go"
    lvlString = ""
    for i in range(lvl.shape[0]):
        for j in range(lvl.shape[1]):
            lvlString += gameCharacters[int(lvl[i][j])]
            if j == lvl.shape[1]-1:
                lvlString += "\n"
    state = State()
    state.stringInitialize(lvlString.split("\n"))

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

class MiniDungeonProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._enemies = kwargs.get("enemies")
        self._solver = kwargs.get("solver", 5000)
        self._diversity = kwargs.get("diversity", 0.4)

        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(8))
        self._control_space = DictionarySpace({"col_treasures": IntegerSpace(self._width + self._height), 
                                               "solution_length": IntegerSpace(2*self._enemies, int(self._width * self._height / 2))})
        self._cerror = {"col_treasures": max(0.2 * (self._width + self._height), 1), 
                        "solution_length": max(0.5 * self._enemies, 1)}

    def info(self, content):
        content = np.array(content)

        regions = get_number_regions(content, [1, 2, 3, 4, 5, 6, 7])
        players = _get_certain_tiles(content, [2])
        layout = get_num_tiles(content, [0,1])
        enemies = _get_certain_tiles(content, [6, 7])
        exits = get_num_tiles(content, [3])
        potions = get_num_tiles(content, [4])
        treasures = get_num_tiles(content, [5])

        heuristic, solution, stats = -1, [], {}
        if regions == 1 and len(players) == 1 and exits == 1:
            heuristic, solution, stats = _run_game(content, self._solver)
        result =  {
            "regions": regions, "players": len(players), "exits": exits, "layout": layout,
            "heuristic": heuristic, "solution": solution, "content": content,
            "potions": potions, "treasures": treasures, "enemies": len(enemies),
            "solution_length": len(solution), "enemies_loc": enemies
        }
        for name in stats:
            result[name] = stats[name]
        return result
    
    def quality(self, info):
        regions = get_range_reward(info["regions"], 0, 1, 1, self._width * self._height / 10)
        player = get_range_reward(info["players"], 0, 1, 1, self._width * self._height)
        exit = get_range_reward(info["exits"], 0, 1, 1, self._width * self._height)
        enemies = get_range_reward(info["enemies"], 0, self._enemies, self._width * self._height)
        layout = get_range_reward(info["layout"], 0, self._width * self._height / 2, self._width * self._height)
        stats = (player + exit + regions + enemies + layout) / 5.0
        solution, enemies = 0, 0
        if player == 1 and exit == 1 and regions == 1:
            solution += get_range_reward(info["heuristic"],0,0,0,(self._width * self._height)**2)
            solution += get_range_reward(len(info["solution"]), 0, self._enemies + 2, (self._width * self._height)**2)
            solution /= 2.0
            
            dist_enemies = []
            for e in info["enemies_loc"]:
                distances = []
                for l in info["solution"]:
                    distances.append(abs(l["x"]-e[0]-1) + abs(l["y"]-e[1]-1)) 
                if len(distances) > 0:   
                    dist_enemies.append(min(distances))
                else:
                    dist_enemies.append(self._width + self._height)
            dist_enemies.sort()
            dist_enemies = dist_enemies[0:self._enemies]
            enemies += get_range_reward(sum(dist_enemies), 0, 0, 0, self._enemies * (self._width + self._height))
            # added += get_range_reward(info["col_enemies"], 0, self._enemies, self._width * self._height)
            # added /= 2.0
        return (stats + solution + enemies) / 3.0
    
    def diversity(self, info1, info2):
        seq1 = _get_solution_sequence(info1["content"], info1["solution"])
        seq2 = _get_solution_sequence(info2["content"], info2["solution"])
        hamming = (abs(info1["content"] - info2["content"]) > 0).sum() / (self._width * self._height)
        seq_score = 1 - SequenceMatcher(None, seq1, seq2).ratio()
        return get_range_reward(seq_score * 0.8 + hamming * 0.2, 0, self._diversity, 1.0)
                
    
    def controlability(self, info, control):
        if info["heuristic"] == -1:
            return 0.0
        treasures = get_range_reward(info["col_treasures"], 0, control["col_treasures"] - self._cerror["col_treasures"], control["col_treasures"] + self._cerror["col_treasures"])
        sol_length = get_range_reward(info["solution_length"], 0, control["solution_length"] - self._cerror["solution_length"], control["solution_length"] + self._cerror["solution_length"])
        return (treasures + sol_length) / 2.0
    
    def render(self, content):
        scale = 16
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/solid.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/player.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/exit.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/potion.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/treasure.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/goblin.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/ogre.png").convert('RGBA'),
        ]
        lvl = np.pad(np.array(content), 1)
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                lvl_image.paste(graphics[lvl[y][x]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        return lvl_image