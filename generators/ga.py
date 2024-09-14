import generators.search as search
import math

class Generator(search.Generator):
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
        search.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def reset(self, **kwargs):
        super().reset(**kwargs)

        self._pop_size = kwargs.get('pop_size', 100)
        self._tournment_size = kwargs.get('tournment_size', 7)
        self._cross_rate = kwargs.get('cross_rate', 0.5)
        self._mut_rate = kwargs.get('mut_rate', 0.05)
        self._elitism = math.ceil(self._pop_size * kwargs.get('elitism_perct', 0.1))

        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(search.Chromosome(self._random))
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