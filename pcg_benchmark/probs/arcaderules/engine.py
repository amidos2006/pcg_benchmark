from enum import Enum
import numpy as np
import math
from pcg_benchmark.probs.utils import _run_dikjstra

def getScript(content):
    behaviors = ["still", "flicker", "randomShort", "randomLong", "wanderHorz", "wanderVert", "chase", "flee"]
    win = ["time", "score5", "score10", "score20"]
    action = ["none", "killFirst", "killSecond", "killBoth"]
    score = [0, 1, 2, 4]

    result = f"Start: {content['x']},{content['y']} - {content['seed']}\n"
    result += "Behavior:\n"
    for key in ["red", "yellow", "green"]:
        locs = ""
        for i in range(content[f"{key}Start"]["num"]):
            locs += f"- {content[f'{key}Start']['x'][i]},{content[f'{key}Start']['y'][i]} "
        result += f"  {key}: {behaviors[int(content[key])]} {locs}\n"
    result += "Rules:\n"
    for key in ["player-red", "player-green", "player-yellow", "red-red", "red-green",\
                "red-yellow", "green-green", "green-yellow", "yellow-yellow"]:
        result += f"  {key}: {action[int(content[key]['action'])]} - {score[int(content[key]['score'])]}\n"
    result +=  f"Win: {win[int(content['win'])]}"
    return result

def runGame(engine, agent):
    result = []
    state = engine.initialize()
    while not(state.isWin() or state.isLose()):
        tempState = state.clone()
        action = agent.action(tempState)
        state.update(action["x"], action["y"])
        result.append((tempState.to_serializable(), action))
    result.append((state.to_serializable(), None))
    return result

class DoNothingAgent:
    def action(self, state):
        return {"x": 0, "y": 0}
    
class RandomAgent:
    def __init__(self, seed):
        self._random = np.random.default_rng(seed)

    def action(self, state):
        return self._random.choice([{"x":-1,"y":0},{"x":1,"y":0},{"x":0,"y":-1},{"x":0,"y":1},{"x":0, "y": 0}])

class FlatMCTSAgent:
    def __init__(self, seed, constant=math.sqrt(2), power=40):
        self._constant = constant
        self._power = power
        self._random = np.random.default_rng(seed)

    def _ucbValue(self, value, totalValue, totalVisits):
        return value["value"] / max(1, totalValue) + self._constant * math.sqrt(math.log(totalVisits) / value["visits"])
    
    def _simulate(self, state):
        while not (state.isWin() or state.isLose()):
            dir = self._random.choice([{"x":-1,"y":0},{"x":1,"y":0},{"x":0,"y":-1},{"x":0,"y":1},{"x":0, "y": 0}])
            state.update(dir["x"], dir["y"])
        if state.isWin():
            return 1
        return 0
    
    def action(self, state):
        dirs = [{"x":-1,"y":0},{"x":1,"y":0},{"x":0,"y":-1},{"x":0,"y":1},{"x":0, "y": 0}]
        total = 0
        visits = 0
        values = []
        for d in dirs:
            nextState = state.clone()
            nextState.update(d["x"], d["y"])
            values.append({"value": self._simulate(nextState.clone()), "visits": 1, "state": nextState})
            visits += 1
            total += values[-1]["value"]
        for _ in range(self._power):
            maxIndex = -1
            maxUCB = -1
            for i,d in enumerate(dirs):
                ucb = self._ucbValue(values[i], total, visits)
                if ucb > maxUCB:
                    maxUCB = ucb
                    maxIndex = i
            v = self._simulate(values[maxIndex]["state"].clone())
            values[maxIndex]["value"] += v
            values[maxIndex]["visits"] += 1
            total += v
            visits += 1
        maxIndex = -1
        maxVisits = -1
        for i,d in enumerate(dirs):
            v = values[i]["visits"]
            if v > maxVisits:
                maxVisits = v
                maxIndex = i
        return dirs[maxIndex]

class Pieces(Enum):
    RED = 0,
    GREEN = 1,
    YELLOW = 2,
    PLAYER = 3

    def get_name(self):
        value = self.value
        if hasattr(value, "__len__"):
            value = value[0]
        return ["red", "green", "yellow", "player"][value]

class State:
    def __init__(self, engine, x, y, score=0, time=0):
        self._engine = engine

        self._player = {"x": x, "y": y, "score": score, "time": time, "alive": True}
        self._reds = []
        self._greens = []
        self._yellows = []
    
    def add(self, t, x, y, state=0, value=0):
        if t == Pieces.RED:
            self._reds.append({"x": x, "y": y, "state": state, "value": value, "alive": True})
        if t == Pieces.GREEN:
            self._greens.append({"x": x, "y": y, "state": state, "value": value, "alive": True})
        if t == Pieces.YELLOW:
            self._yellows.append({"x": x, "y": y, "state": state, "value": value, "alive": True})

    def clone(self):
        state = State(self._engine, self._player["x"], self._player["y"], self._player["score"], self._player["time"])
        state._player["alive"] = self._player["alive"]
        for i,obj in enumerate(self._reds):
            state.add(Pieces.RED, obj["x"], obj["y"], obj["state"], obj["value"])
            state._reds[i]["alive"] = self._reds[i]["alive"]
        for i,obj in enumerate(self._greens):
            state.add(Pieces.GREEN, obj["x"], obj["y"], obj["state"], obj["value"])
            state._greens[i]["alive"] = self._greens[i]["alive"]
        for i,obj in enumerate(self._yellows):
            state.add(Pieces.YELLOW, obj["x"], obj["y"], obj["state"], obj["value"])
            state._yellows[i]["alive"] = self._yellows[i]["alive"]
        return state

    def update(self, dx, dy):
        if not (self.isWin() or self.isLose()):
            self._player["time"] += 1
            self._engine.move(self._player, dx, dy)
            for obj in self._reds:
                self._engine.updateBehavior(Pieces.RED, obj, self._player["x"], self._player["y"])
            for obj in self._greens:
                self._engine.updateBehavior(Pieces.GREEN, obj, self._player["x"], self._player["y"])
            for obj in self._yellows:
                self._engine.updateBehavior(Pieces.YELLOW, obj, self._player["x"], self._player["y"])
            
            for obj in self._reds:
                if obj["alive"]:
                    self._player["score"] += self._engine.updateCollision(Pieces.PLAYER, Pieces.RED, self._player, obj)
            for obj in self._greens:
                if obj["alive"]:
                    self._player["score"] += self._engine.updateCollision(Pieces.PLAYER, Pieces.GREEN, self._player, obj)
            for obj in self._yellows:
                if obj["alive"]:
                    self._player["score"] += self._engine.updateCollision(Pieces.PLAYER, Pieces.YELLOW, self._player, obj)
            for obj1 in self._reds:
                for obj2 in self._reds:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.RED, Pieces.RED, obj1, obj2)
                for obj2 in self._greens:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.RED, Pieces.GREEN, obj1, obj2)
                for obj2 in self._yellows:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.RED, Pieces.YELLOW, obj1, obj2)
            for obj1 in self._greens:
                for obj2 in self._greens:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.GREEN, Pieces.GREEN, obj1, obj2)
                for obj2 in self._yellows:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.GREEN, Pieces.YELLOW, obj1, obj2)
            for obj1 in self._yellows:
                for obj2 in self._yellows:
                    if obj1 != obj2 and obj1["alive"] and obj2["alive"]:
                        self._player["score"] += self._engine.updateCollision(Pieces.YELLOW, Pieces.YELLOW, obj1, obj2)
    
    def isWin(self):
        return self._engine.checkWin(self._player["score"], self._player["time"])

    def isLose(self):
        return self._engine.checkLose(self._player["alive"], self._player["time"])

    def __str__(self):
        result = f"{self._player['time']}-{self._player['x']},{self._player['y']},{self._player['score']},{self._player['alive']}"
        for obj in self._reds:
            result += f"-{Pieces.RED}:{obj['x']},{obj['y']},{obj['state']},{obj['value']},{obj['alive']}"
        for obj in self._greens:
            result += f"-{Pieces.GREEN}:{obj['x']},{obj['y']},{obj['state']},{obj['value']},{obj['alive']}"
        for obj in self._yellows:
            result += f"-{Pieces.YELLOW}:{obj['x']},{obj['y']},{obj['state']},{obj['value']},{obj['alive']}"
        return result
    
    def to_serializable(self):
        return {
            '_player': self._player,
            '_reds': self._reds,
            '_yellows': self._yellows,
            '_greens': self._greens,
            'isWin': self.isWin(),
            'isLose': self.isLose(),
        }

class Engine:
    def __init__(self, content, layout, maxTime=40):
        self._content = content
        self._maxTime = maxTime
        self._layout = np.pad(np.array(layout), 1)
        needDijkstra = False
        for key in ["red", "green", "yellow"]:
            if (self._content[key] == 6 or self._content[key] == 7) and self._content[f"{key}Start"]["num"] > 0:
                needDijkstra = True
        self._dikjstra = {}
        if needDijkstra:
            for y in range(self._layout.shape[0]):
                for x in range(self._layout.shape[1]):
                    if self._layout[y][x] == 1:
                        self._dikjstra[f"{x},{y}"] = _run_dikjstra(x, y, self._layout, [1])[0]
    
    def initialize(self):
        self._random = np.random.default_rng(self._content["seed"])
        state = State(self, self._content["x"] + 1, self._content["y"] + 1)
        for i in range(self._content["redStart"]["num"]):
            x, y = self._content["redStart"]["x"][i]+1, self._content["redStart"]["y"][i]+1
            if self._layout[y][x] == 1:
                state.add(Pieces.RED, x, y)
        for i in range(self._content["greenStart"]["num"]):
            x, y = self._content["greenStart"]["x"][i]+1, self._content["greenStart"]["y"][i]+1
            if self._layout[y][x] == 1:
                state.add(Pieces.GREEN, x, y)
        for i in range(self._content["yellowStart"]["num"]):
            x, y = self._content["yellowStart"]["x"][i]+1, self._content["yellowStart"]["y"][i]+1
            if self._layout[y][x] == 1:
                state.add(Pieces.YELLOW, x, y)
        return state
    
    def move(self, obj, dx, dy):
        nx, ny = obj["x"] + dx, obj["y"] + dy
        if nx >= 0 and nx < self._layout.shape[1] and ny>=0 and ny < self._layout.shape[0] and self._layout[ny][nx] == 1:
            obj["x"], obj["y"] = nx, ny
            return True
        return False

    def updateBehavior(self, t, obj, px, py):
        if not obj["alive"] and self._content[t.get_name()] != 1:
            return
        obj["value"] += 1
        if self._content[t.get_name()] == 1:
            obj["alive"] = int(obj["value"] / 5) % 2 == 0
        if self._content[t.get_name()] == 2:
            if obj["value"] % 5 == 1: 
                obj["state"] = self._random.integers(4)
            dir = [{"x":-1,"y":0},{"x":1,"y":0},{"x":0,"y":-1},{"x":0,"y":1}][obj["state"]]
            self.move(obj, dir["x"], dir["y"])
        if self._content[t.get_name()] == 3:
            if obj["value"] % 10 == 1: 
                obj["state"] = self._random.integers(4)
            dir = [{"x":-1,"y":0},{"x":1,"y":0},{"x":0,"y":-1},{"x":0,"y":1}][obj["state"]]
            self.move(obj, dir["x"], dir["y"])
        if self._content[t.get_name()] == 4:
            if obj["value"] == 1:
                obj["state"] = self._random.integers(2)
            dir = [{"x":-1,"y":0},{"x":1,"y":0}][obj["state"]]
            moved = self.move(obj, dir["x"], dir["y"])
            if not moved:
                obj["state"] = 1 - obj["state"]
                self.move(obj, dir["x"], dir["y"])
        if self._content[t.get_name()] == 5:
            if obj["value"] == 1:
                obj["state"] = self._random.integers(2)
            dir = [{"x":0,"y":-1},{"x":0,"y":1}][obj["state"]]
            moved = self.move(obj, dir["x"], dir["y"])
            if not moved:
                obj["state"] = 1 - obj["state"]
                self.move(obj, dir["x"], dir["y"])
        if self._content[t.get_name()] == 6 or self._content[t.get_name()] == 7:
            dikjstra = self._dikjstra[f"{px},{py}"]
            dir = [{"x":-1,"y":0,"value":10000},{"x":1,"y":0,"value":10000},{"x":0,"y":-1,"value":10000},{"x":0,"y":1,"value":10000}]
            for d in dir:
                d["value"] = dikjstra[obj["y"] + d["y"]][obj["x"] + d["x"]]
            dir.sort(key=lambda x: x["value"], reverse=self._content[t.get_name()] == 7)
            self.move(obj, dir[0]["x"], dir[0]["y"])
    
    def updateCollision(self, t1, t2, obj1, obj2):
        if obj1["x"] == obj2["x"] and obj1["y"] == obj2["y"]:
            index = f"{t1.get_name()}-{t2.get_name()}"
            if self._content[index]["action"] == 1:
                obj1["alive"] = False
            if self._content[index]["action"] == 2:
                obj2["alive"] = False
            if self._content[index]["action"] == 3:
                obj1["alive"] = False
                obj2["alive"] = False
            if self._content[index]["score"] == 3:
                return 4
            return self._content[index]["score"]
        return 0
    
    def checkWin(self, score, time):
        if self._content["win"] == 1:
            return score >= 5
        if self._content["win"] == 2:
            return score >= 10
        if self._content["win"] == 3:
            return score >= 20
        return time >= self._maxTime
    
    def checkLose(self, alive, time):
        if self._content["win"] != 0:
            return time >= self._maxTime
        return not alive
    
