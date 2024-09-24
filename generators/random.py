import generators.search as search

class Generator(search.Generator):
    def reset(self, **kwargs):
        super().reset(**kwargs)

        self._pop_size = kwargs.get('pop_size', 100)

        self._chromosomes = []
        for _ in range(self._pop_size):
            self._chromosomes.append(search.Chromosome(self._random))
            self._chromosomes[-1].random(self._env)
        search.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        while len(chromosomes) < self._pop_size:
            child = search.Chromosome(self._random)
            child.random(self._env)
            chromosomes.append(child)
        search.evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._pop_size]
