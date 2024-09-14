import generators.search as search

class Generator(search.Generator):
    def reset(self, **kwargs):
        super().reset(**kwargs)

        self._mu_size = kwargs.get('mu_size', 100)
        self._lambda_size = kwargs.get('lambda_size', 100)
        self._mut_rate = kwargs.get('mut_rate', 0.05)

        self._chromosomes = []
        for _ in range(self._mu_size):
            self._chromosomes.append(search.Chromosome(self._random))
            self._chromosomes[-1].random(self._env)
        search.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        for i in range(self._lambda_size):
            index = self._random.integers(self._mu_size)
            chromosomes.append(self._chromosomes[index].mutation(self._env, self._mut_rate))
        search.evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._mu_size]
