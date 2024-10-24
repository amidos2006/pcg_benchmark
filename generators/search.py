
import generators.generator as base
import os
import shutil
import json
import numpy as np
from pcg_benchmark.spaces import contentSwap
import sys

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

class Chromosome:
    def __init__(self, random=None):
        if random:
            self._random = random
        else:
            self._random = np.random.default_rng()
        self._content = None
        self._control = None

        self._info = None
        self._quality = None
        self._diversity = None
        self._controlability = None

    def random(self, env):
        self._content = env.content_space.sample()
        self._control = env.control_space.sample()

    def crossover(self, chromosome):
        child = Chromosome(self._random)
        child._content = contentSwap(self._content, chromosome._content, 0.5, -1, self._random)
        child._control = [self._control, chromosome._control][self._random.integers(2)]
        return child

    def mutation(self, env, mut_rate):
        child = Chromosome(self._random)
        child._content = contentSwap(self._content, env.content_space.sample(), mut_rate, -1, self._random)
        child._control = self._control
        return child
    
    def quality(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._quality
    
    def diversity(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._diversity

    def controlability(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._controlability
    
    def save(self, filepath):
        savedObject = {
            "content": self._content,
            "control": self._control,
            "info": self._info,
            "quality": self._quality,
            "diversity": self._diversity,
            "controlability": self._controlability
        }
        with open(filepath, 'w') as f:
            f.write(json.dumps(savedObject, cls=NpEncoder))
    
    def load(self, filepath):
        with open(filepath, 'r') as f:
            savedObject = json.loads("".join(f.readlines()))
            self._content = savedObject["content"]
            self._control = savedObject["control"]
            self._info = savedObject["info"]
            self._quality = savedObject["quality"]
            self._diversity = savedObject["diversity"]
            self._controlability = savedObject["controlability"]

class Generator(base.Generator):
    def reset(self, **kwargs):
        super().reset(**kwargs)

        fn_name = kwargs.get('fitness', 'fitness_quality')
        if hasattr(sys.modules[__name__], fn_name):
            self._fitness_fn = getattr(sys.modules[__name__], fn_name)
        elif hasattr(sys.modules[__name__], f"fitness_{fn_name}"):
            self._fitness_fn = getattr(sys.modules[__name__], f"fitness_{fn_name}")
        else:
            raise ValueError(f"{fn_name} doesn't exits in generators.search.py file")

        self._chromosomes = []

    def best(self):
        return self._fitness_fn(self._chromosomes[0])

    def save(self, folderpath):
        if os.path.exists(folderpath):
            shutil.rmtree(folderpath)
        os.makedirs(folderpath)
        for i in range(len(self._chromosomes)):
            self._chromosomes[i].save(os.path.join(folderpath, f"chromosome_{i}.json"))
    
    def load(self, folderpath):
        files = [os.path.join(folderpath, fn) for fn in os.listdir(folderpath) if "chromosome" in fn]
        self._chromosomes = []
        for fn in files:
            c = base.Chromosome(self._random)
            c.load(fn)
            self._chromosomes.append(c)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

def evaluateChromosomes(env, chromosomes):
    content = [c._content for c in chromosomes]
    control = [c._control for c in chromosomes]
    _, _, _, details, info = env.evaluate(content, control)
    for i in range(len(chromosomes)):
        chromosomes[i]._quality = details["quality"][i]
        chromosomes[i]._diversity = details["diversity"][i]
        chromosomes[i]._controlability = details["controlability"][i]
        chromosomes[i]._info = info[i]

def fitness_quality(chromosome):
    return chromosome.quality()

def fitness_quality_control(chromosome):
    result = chromosome.quality()
    if chromosome.quality() >= 1:
        result += chromosome.controlability()
    return result / 2.0

def fitness_quality_control_diversity(chromosome):
    result = chromosome.quality()
    if chromosome.quality() >= 1:
        result += chromosome.controlability()
    if chromosome.quality() >= 1 and chromosome.controlability() >= 1:
        result += chromosome.diversity()
    return result / 3.0