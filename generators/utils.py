from pcg_benchmark.spaces import swapContent

class Chromosome:
    def __init__(self, env, mut_rate):
        self._env = env
        self._mut_rate = mut_rate

        self._content = None
        self._target = None

        self._info = None
        self._fitness = None
        self._diversity = None
        self._control = None

    def random(self):
        self._content = self._env.content_space.sample()
        self._target = self._env.control_space.sample()

    def crossover(self, chromosome):
        child = Chromosome(self._env, self._mut_rate)
        child._content = swapContent(self._content, chromosome._content, 0.5)
        return child

    def mutation(self):
        child = Chromosome(self._env, self._mut_rate)
        child._content = swapContent(self._content, self._env.content_space.sample(), self._mut_rate)
        return child
    
    def fitness(self):
        if self._info == None:
            self._info = self._env.info(self._content)
        return self._env.fitness(self._info)
    
    def distance(self, chromosome):
        if self._info == None:
            self._info = self._env.info(self._content)
        if chromosome._info == None:
            chromosome._info = chromosome._env.info(self._content)
        return self._env.diversity([self._info, chromosome._info])
    
    def control(self):
        if self._info == None:
            self._info = self._env.info(self._content)
        if self._control == None:
            return 0
        return self._env.control(self._info, self._control)