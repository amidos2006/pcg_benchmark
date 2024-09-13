import generators.utils as utils
import math
import os
import shutil

class Generator(utils.Generator):
    def __init__(self, env, fitness_fn, pop_size=100, tournment_size=7, cross_rate=0.5, mut_rate=0.05, elitism_perct=0.1):
        super().__init__(env, fitness_fn)

        self._pop_size = pop_size
        self._tournment_size = tournment_size
        self._cross_rate = cross_rate
        self._mut_rate = mut_rate
        self._elitism = math.ceil(pop_size * elitism_perct)
        self._chromosomes = []

    def _select(self):
        size= self._tournment_size
        if size > self._pop_size:
            size = self._pop_size
        tournment = list(range(self._pop_size))
        self._random.shuffle(tournment)
        chromosomes = []
        for i in range(size):
            chromosomes.append(self._chromosomes[tournment[i]])
        chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        return chromosomes[0]
    
    def _evaluate(self):
        utils.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def reset(self, seed=None):
        super().reset(seed)

        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(utils.Chromosome(self._random))
            self._chromosomes[-1].random(self._env)
        self._evaluate()

    def update(self):
        chromosomes = []
        for i in range(self._elitism):
            chromosomes.append(self._chromosomes[i])
        while len(chromosomes) < self._pop_size:
            child = self._select()
            if self._random.random() < self._cross_rate:
                parent = self._select()
                child = child.crossover(parent)
            child = child.mutation(self._env, self._mut_rate)
            chromosomes.append(child)
        self._chromosomes = chromosomes
        self._evaluate()

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