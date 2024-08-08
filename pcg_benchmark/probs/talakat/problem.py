from pcg_benchmark.probs import Problem
from pcg_benchmark.probs.utils import get_range_reward
from pcg_benchmark.spaces import ArraySpace, IntegerSpace, FloatSpace, DictionarySpace
from pcg_benchmark.probs.talakat.engine import parameters, generateTalakatScript, runPattern
from pcg_benchmark.probs.talakat.engine.helper import ActionNumber, calculateBuckets, calculateEntropy
import numpy as np
from PIL import Image, ImageDraw
import os

class TalakatProblem(Problem):
    def __init__(self, **kwargs):
        Problem.__init__(self, **kwargs)
        self._width = kwargs.get("width")
        self._height = kwargs.get("height")
        self._spawnerComplexity = kwargs.get("spawnerComplexity")
        self._maxHealth = kwargs.get("maxHealth")
        
        self._agentPrecision = kwargs.get("precision", 10)
        self._diversity = kwargs.get("diversity", 0.5)
        self._diversitySampling = kwargs.get("diversitySampling", 5)
        self._renderSampling = kwargs.get("renderSampling", 5)

        parameters["maxHealth"] = self._maxHealth
        parameters["repeatingAction"] = self._agentPrecision
        parameters["width"] = self._width
        parameters["height"] = self._height

        self._target = 0.25
        self._cerror = 0.1

        self._content_space = ArraySpace((self._spawnerComplexity, 100), IntegerSpace(100))
        self._control_space = DictionarySpace({
            "bullet_coverage": FloatSpace(self._target+self._cerror, 1-self._cerror)
        })
    
    def info(self, content):
        script = generateTalakatScript(content)
        connections = set()
        nextSpawners = ["spawner_0"]
        while len(nextSpawners) > 0:
            currentSpawner = nextSpawners.pop(0)
            for spawned in script["spawners"][currentSpawner]["pattern"]:
                if "spawner_" in spawned:
                    if not spawned in connections:
                        connections.update([spawned])
                        nextSpawners.append(spawned)
        result = runPattern(script)
        
        bullets = []
        coverage = np.zeros(parameters["bucketsX"] * parameters["bucketsY"])
        for world, _ in result:
            temp = np.array(calculateBuckets(self._width, self._height, parameters["bucketsX"], parameters["bucketsY"], world.bullets))
            bullets.append(temp / max(1, temp.sum()))
            coverage += temp / max(1, temp.sum())

        return {
            "script_connectivity": (len(connections) + 1) / self._spawnerComplexity,
            "percentage": len(result) / self._maxHealth,
            "bullet_coverage": calculateEntropy(coverage / self._maxHealth),
            "bullet_locations": bullets,
        }
    
    def quality(self, info):
        playable = info["percentage"]
        coverage = 0.0
        if playable >= 1.0:
            coverage = get_range_reward(info["bullet_coverage"], 0, self._target, 1)
        return (playable + coverage) / 2.0
    
    def diversity(self, info1, info2):
        diversity = []
        for i in range(self._diversitySampling):
            index1 = int(min(self._maxHealth * i / (self._diversitySampling - 1), len(info1["bullet_locations"]) - 1))
            index2 = int(min(self._maxHealth * i / (self._diversitySampling - 1), len(info2["bullet_locations"]) - 1))
            diversity.append(abs(info1["bullet_locations"][index1] - info2["bullet_locations"][index2]).sum() / 2.0)
        return get_range_reward(np.array(diversity).max(), 0, self._diversity, 1)
    
    def controlability(self, info, control):
        bulletCoverage = get_range_reward(info["bullet_coverage"], 0,\
            control["bullet_coverage"] - self._cerror, control["bullet_coverage"] + self._cerror, 1)
        return bulletCoverage
    
    def render(self, content):
        bossGfx = Image.open(os.path.dirname(__file__) + "/images/boss.png").convert('RGBA')
        result = runPattern(generateTalakatScript(content))
        images = []
        for i in range(0, len(result), self._renderSampling):
            img = Image.new("RGBA", (parameters["width"], parameters["height"]), (71,45,60,255))
            draw = ImageDraw.Draw(img)
            draw.rectangle([0,0,img.width,img.height], fill=(71,45,60,255))
            for b in result[i][0].bullets:
                draw.ellipse([b.x - b.radius, b.y - b.radius, b.x + b.radius, b.y + b.radius], fill=(207,198,184,255), outline=(230,72,46,255), width=2)
            img.paste(bossGfx, (int(result[i][0].boss.x - bossGfx.width/2), int(result[i][0].boss.y-bossGfx.height/2),\
                                int(result[i][0].boss.x+bossGfx.width/2), int(result[i][0].boss.y+bossGfx.height/2)), bossGfx)
            images.append(img)
        images[0].save(os.path.dirname(__file__) + "/images/temp.gif", save_all=True, optimize=False, append_images=images[1:], duration=100, loop=0)
        gif_img = Image.open(os.path.dirname(__file__) + "/images/temp.gif")
        os.remove(os.path.dirname(__file__) + "/images/temp.gif")
        return gif_img