import generators.utils as utils
import os
import shutil

class Generator(utils.Generator):
    def __init__(self, env, fitness_fn, mu_size=100, lambda_size=100, mut_rate=0.05):
        super().__init__(env, fitness_fn)

        self._mu_size = mu_size
        self._lambda_size = lambda_size
        self._mut_rate = mut_rate
        self._chromosomes = []
    
    def reset(self, seed=None):
        super().reset(seed)

        self._chromosomes = []
        for _ in range(self._mu_size):
            self._chromosomes.append(utils.Chromosome(self._random))
            self._chromosomes[-1].random(self._env)
        utils.evaluateChromosomes(self._env, self._chromosomes)
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)

    def update(self):
        chromosomes = []
        for i in range(self._lambda_size):
            index = self._random.integers(self._lambda_size)
            chromosomes.append(self._chromosomes[index].mutation(self._env, self._mut_rate))
        utils.evaluateChromosomes(self._env, chromosomes)
        self._chromosomes = self._chromosomes + chromosomes
        self._chromosomes.sort(key=lambda c: self._fitness_fn(c), reverse=True)
        self._chromosomes = self._chromosomes[:self._mu_size]

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
