from pcg_benchmark.probs import Problem
from pcg_benchmark.probs.utils import get_range_reward
from pcg_benchmark.spaces import DictionarySpace, ArraySpace, IntegerSpace
import os
import numpy as np
from PIL import Image

def _random_control(self):
    target = self.range()["1x1"]["max"]
    control = DictionarySpace.sample(self)
    sum_all = 0
    for k in control:
        sum_all += control[k]
    remaining = target
    for k in control:
        control[k] = int((control[k] / sum_all) * target)
        remaining -= control[k]
    control[self._random.choice(list(control.keys()))] += remaining
    return control

def _orient(lvl, width, length, height):
    shift_x,shift_y,shift_width,shift_height=width,length,0,0
    for z in range(height):
        v_x, v_y = [], []
        for y in range(length):
            for x in range(width):
                if lvl[z][y][x]:
                    v_x.append(x)
                    v_y.append(y)
        if len(v_x) > 0:
            shift_x = min(shift_x, min(v_x))
            shift_width = max(shift_width, max(v_x) - shift_x)
        if len(v_y) > 0:
            shift_y = min(shift_y, min(v_y))
            shift_height = max(shift_height, max(v_y) - shift_y)
    if shift_height > shift_width:
        lvl = np.transpose(lvl, axes=[0,2,1])
    new_lvl = lvl.copy()
    for z in range(height):
        for y in range(length):
            for x in range(width):
                new_lvl[z][y-shift_y][x-shift_x] = lvl[z][y][x]
    return new_lvl

def _simulate(content, width, length, height):
    result, heights, failed = np.zeros((height, length, width)).astype(int), [], 0
    shapes = [np.array([[1]]), np.array([[1,1,1]]), np.array([[1],[1],[1]]), np.array([[1,1,1],[1,1,1],[1,1,1]])]

    for block in content:
        x,y,t = block["x"],block["y"],block["type"]
        sh = shapes[t]
        sx, sy = min(x, width-sh.shape[1]), min(y, length-sh.shape[0])
        ex, ey = min(width, x+sh.shape[1]), min(length, y+sh.shape[0])
        z = height
        moveDown = True
        while moveDown and z > 0:
            for y in range(sy,ey):
                for x in range(sx,ex):
                    if result[z-1][y][x] > 0:
                        moveDown = False
            if moveDown:
                z -= 1
        z = max(0, z)
        if z < height:
            for y in range(sy,ey):
                for x in range(sx,ex):
                    result[z][y][x] = t + 1
        else:
            failed += 1 
    for y in range(length):
        for x in range(width):
            found = False
            for z in range(height-1, -1, -1):
                if found:
                    if result[z][y][x] == 0:
                        found = False
                else:
                    if result[z][y][x] > 0:
                        heights.append(z+1)
                        found = True
    return result, heights, failed

class BuildingProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)

        self._width = kwargs.get("width")
        self._length = kwargs.get("length")
        self._height = kwargs.get("height")
        self._target = kwargs.get("blocks", self._width * self._length * self._height / 9)
        self._min_height = kwargs.get("minHeight", 0.4)
        self._diversity = kwargs.get("diversity", 0.4)

        self._cerror = max(1, int(0.05 * self._target))

        self._content_space = ArraySpace((self._target), DictionarySpace({
            "x": IntegerSpace(self._width),
            "y": IntegerSpace(self._length),
            "type": IntegerSpace(4)
        }))
        self._control_space = DictionarySpace({
            "1x1": IntegerSpace(self._target),
            "1x3": IntegerSpace(self._target),
            "3x1": IntegerSpace(self._target),
            "3x3": IntegerSpace(self._target)
        })
        self._control_space.sample = _random_control.__get__(self._control_space, DictionarySpace)
        
    def info(self, content):
        lvl, heights, failing = _simulate(content, self._width, self._length, self._height)
        values = [0, 0, 0, 0]
        for block in content:
            values[block["type"]] += 1
        return {
            "blocks": self._target - failing,
            "heights": heights,
            "lvl_1x1": _orient(lvl == 1, self._width, self._length, self._height).astype(int),
            "lvl_1x3": _orient(lvl == 2, self._width, self._length, self._height).astype(int),
            "lvl_3x1": _orient(lvl == 3, self._width, self._length, self._height).astype(int),
            "lvl_3x3": _orient(lvl == 4, self._width, self._length, self._height).astype(int),
            "1x1": values[0],
            "1x3": values[1],
            "3x1": values[2],
            "3x3": values[3]
        }
    
    def quality(self, info):
        target = get_range_reward(info["blocks"], 0, self._target)
        min_height = 0
        if target >= 1:
            for i in range(int(self._min_height * self._height)):
                heights = [h for h in info["heights"] if h == i + 1]
                if len(heights) > 0:
                    min_height += get_range_reward(len(heights), 0, 0, 0, self._width * self._length)
                    break
                min_height += 1
            min_height /= int(self._min_height * self._height)
        return (target + min_height) / 2
    
    def diversity(self, info1, info2):
        diversity = abs(info1["lvl_1x1"] - info2["lvl_1x1"]).sum()
        diversity += abs(info1["lvl_1x3"] - info2["lvl_1x3"]).sum()
        diversity += abs(info1["lvl_3x1"] - info2["lvl_3x1"]).sum()
        diversity += abs(info1["lvl_3x3"] - info2["lvl_3x3"]).sum()
        return get_range_reward(diversity, 0, self._diversity * self._width * self._length * self._height,\
            self._width * self._length * self._height)

    def controlability(self, info, control):
        b1x1 = get_range_reward(info["1x1"], 0, control["1x1"]-self._cerror, control["1x1"]+self._cerror, self._target)
        b1x3 = get_range_reward(info["1x3"], 0, control["1x3"]-self._cerror, control["1x3"]+self._cerror, self._target)
        b3x1 = get_range_reward(info["3x1"], 0, control["3x1"]-self._cerror, control["3x1"]+self._cerror, self._target)
        b3x3 = get_range_reward(info["3x3"], 0, control["3x3"]-self._cerror, control["3x3"]+self._cerror, self._target)
        return (b1x1 + b1x3 + b3x1 + b3x3) / 4

    def render(self, content):
        scale_x = 16
        scale_y = 8
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/1x1.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/1x3.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/3x1.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/3x3.png").convert('RGBA'),
        ]
        mask = Image.open(os.path.dirname(__file__) + "/images/1x1.png").convert('RGBA')
        lvl, _, _ = _simulate(content, self._width, self._length, self._height)
        image = Image.new("RGBA", (int((self._width + self._length)*scale_x / 2), int((2*self._height+ self._length+ self._width+1)*scale_y/2)), (0,0,0,255))
        shift_x, shift_y = (self._length-1)*scale_x/2, (self._height-1)*scale_y
        for x in range(self._width):
            for y in range(self._length):
                for z in range(self._height):
                    sx, sy = int((x-y)*scale_x/2+shift_x), int((x+y-2*z)*scale_y/2+shift_y)
                    if lvl[z][y][x] > 0:
                        graphics[lvl[z][y][x]-1].putalpha(255 - int(100 * y/self._length))
                        image.paste(graphics[lvl[z][y][x]-1], (sx, sy, sx+16, sy+16), mask)
                        graphics[lvl[z][y][x]-1].putalpha(255)
        return image