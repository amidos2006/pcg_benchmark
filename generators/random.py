import generators.utils as utils
import os
import shutil

class Generator(utils.Generator):
    def __init__(self, env, fitness_fn, pop_size=100):
        super().__init__(env, fitness_fn)

        self._pop_size = pop_size
        self._chromosomes = []
    
    def reset(self, seed=None):
        super().reset(seed)

        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(utils.Chromosome(self._random))
            self._chromosomes[-1].random(self._env)
        utils.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        while len(chromosomes) < self._pop_size:
            child = utils.Chromosome()
            child.random(self._env)
            chromosomes.append(child)
        utils.evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._pop_size]

    def save(self, folderpath):
        if os.path.exists(folderpath):
            shutil.rmtree(folderpath)
        os.makedirs(folderpath)
        for i in range(len(self._chromosomes)):
            self._chromosomes[i].save(os.path.join(folderpath, f"chromsome_{i}.json"))
    
    def load(self, folderpath):
        files = [os.path.join(folderpath, fn) for fn in os.listdir(folderpath) if "chromosome" in fn]
        self._chromosomes = []
        for fn in files:
            c = utils.Chromosome(self._random)
            c.load(fn)
            self._chromosomes.append(c)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
