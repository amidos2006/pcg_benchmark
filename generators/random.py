from .utils import Chromosome, evaluateChromosomes
import math
import numpy as np

class RandomSearch:
    def __init__(self, env, fitness_fn, pop_size=100):
        self._env = env
        self._fitness_fn = fitness_fn
        self._random = np.random.default_rng()
        self._pop_size = pop_size
        self._chromosomes = []
    
    def reset(self, seed=None):
        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(Chromosome())
            self._chromosomes[-1].random(self._env)
        if seed:
            self._random = np.random.default_rng(seed)
        evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        while len(chromosomes) < self._pop_size:
            child = Chromosome()
            child.random(self._env)
            chromosomes.append(child)
        evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._pop_size]
