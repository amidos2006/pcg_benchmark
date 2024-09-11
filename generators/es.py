from .utils import Chromosome, evaluateChromosomes
import math
import numpy as np

class ES:
    def __init__(self, env, fitness_fn, mu_size=100, lambda_size=100, mut_rate=0.05):
        self._env = env
        self._fitness_fn = fitness_fn
        self._random = np.random.default_rng()
        self._mu_size = mu_size
        self._lambda_size = lambda_size
        self._mut_rate = mut_rate
        self._chromosomes = []
    
    def reset(self, seed=None):
        self._chromosomes = []
        for _ in range(self._mu_size):
            self._chromosomes.append(Chromosome())
            self._chromosomes[-1].random(self._env)
        if seed:
            self._random = np.random.default_rng(seed)
        evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        for i in range(self._lambda_size):
            index = self._random.integers()
            chromosomes.append(self._chromosomes[index].mutate(self._mut_rate))
        evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._pop_size]