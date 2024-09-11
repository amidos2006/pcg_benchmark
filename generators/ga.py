from .utils import Chromosome, evaluateChromosomes
import math
import numpy as np

class GA:
    def __init__(self, env, fitness_fn, pop_size=100, tournment_size=7, cross_rate=0.5, mut_rate=0.05, elitism_perct=0.1):
        self._env = env
        self._fitness_fn = fitness_fn
        self._random = np.random.default_rng()
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
            chromosomes.append(tournment[i])
        chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        return chromosomes[0]
    
    def _evaluate(self):
        evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
    
    def reset(self, seed=None):
        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(Chromosome())
            self._chromosomes[-1].random(self._env)
        if seed:
            self._random = np.random.default_rng(seed)
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
            child = child.mutate(self._env, self._mut_rate)
            chromosomes.append(child)
        self._chromosomes = chromosomes
        self._evaluate()

    def best(self):
        return self._chromosomes[0]
    
    def content(self):
        return [c._content for c in self._chromosomes]
    
    def control(self):
        return [c._control for c in self._chromosomes]
    
    def quality(self):
        return [c.quality() for c in self._chromosomes]
    
    def diversity(self):
        return [c.diversity() for c in self._chromosomes]
    
    def controlability(self):
        return [c.controlability() for c in self._chromosomes]

def fitness_quality(chromosome):
    return chromosome.fitness()

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