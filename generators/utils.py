from pcg_benchmark.spaces import contentSwap
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

class Generator:
    def __init__(self, env, fitness_fn):
        self._env = env
        self._fitness_fn = fitness_fn
        self._random = np.random.default_rng()

    def reset(self, seed=None):
        if seed:
            self._random = np.random.default_rng(seed)

    def update(self):
        return NotImplementedError("The update function is not implemented, please make sure to implment it.")
    
    def save(self, folderpath):
        raise NotImplementedError("The save function is not implemented, please make sure to implment it.")
    
    def load(self, folderpath):
        return NotImplementedError("The load function is not implemented, please make sure to implment it.")

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
        child = Chromosome()
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
    if chromosome.controlability() >= 1:
        result += chromosome.diversity()
    return result / 3.0