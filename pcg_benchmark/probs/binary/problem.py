from pcg_benchmark.probs import Problem
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, DictionarySpace
from pcg_benchmark.probs.utils import get_range_reward, get_number_regions, get_longest_path
import numpy as np
from PIL import Image
import os

class BinaryProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)
        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._target = kwargs.get("path", self._width + self._height)
        self._diversity = kwargs.get("diversity", 0.4)

        self._cerror = max(int(self._target * 0.25), 1)
        self._content_space = ArraySpace((self._height, self._width), IntegerSpace(2))
        self._control_space = DictionarySpace({"path": IntegerSpace(self._target + self._cerror, int(self._width * self._height / 2))})

    def info(self, content):
        content = np.array(content)
        number_regions = get_number_regions(content, [1])
        longest = get_longest_path(content, [1])

        return {"path": longest, "regions": number_regions, "flat": content.flatten()}

    def quality(self, info):
        number_regions = get_range_reward(info["regions"], 0, 1, 1, self._width * self._height / 10)
        longest = get_range_reward(info["path"], 0, self._target, self._width * self._height)
        return (number_regions + longest) / 2
    
    def diversity(self, info1, info2):
        hamming = abs(info1["flat"] - info2["flat"]).sum()
        return get_range_reward(hamming, 0, self._diversity * self._width * self._height, self._width * self._height)
    
    def controlability(self, info, control):
        longest = get_range_reward(info["path"], 0, control["path"]-self._cerror, control["path"]+self._cerror, self._width * self._height)
        return longest
    
    def render(self, content):
        scale = 16
        graphics = [
            Image.open(os.path.dirname(__file__) + "/images/solid.png").convert('RGBA'),
            Image.open(os.path.dirname(__file__) + "/images/empty.png").convert('RGBA')
        ]
        lvl = np.pad(np.array(content), 1)
        lvl_image = Image.new("RGBA", (lvl.shape[1]*scale, lvl.shape[0]*scale), (0,0,0,255))
        for y in range(lvl.shape[0]):
            for x in range(lvl.shape[1]):
                lvl_image.paste(graphics[lvl[y][x]], (x*scale, y*scale, (x+1)*scale, (y+1)*scale))
        return lvl_image