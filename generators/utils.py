from pcg_benchmark.spaces import swapContent

class Chromosome:
    def __init__(self):
        self._content = None
        self._control = None

        self._info = None
        self._quality = None
        self._diversity = None
        self._controlability = None

    def random(self, env):
        self._content = env.content_space.sample()
        self._control = env.control_space.sample()

    def crossover(self, chromosome):
        child = Chromosome()
        child._content = swapContent(self._content, chromosome._content, 0.5)
        return child

    def mutation(self, env, mut_rate):
        child = Chromosome()
        child._content = swapContent(self._content, env.content_space.sample(), mut_rate)
        return child
    
    def quality(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._quality
    
    def diversity(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._diversity

    def controlability(self):
        if self._info == None:
            raise ValueError("You need to compute all the values first")
        return self._controlability
    
def evaluateChromosomes(env, chromosomes):
    content = [c._content for c in chromosomes]
    control = [c._control for c in chromosomes]
    _, _, _, details, info = env.evaluate(content, control)
    for i in range(len(chromosomes)):
        chromosomes[i]._quality = details["quality"][i]
        chromosomes[i]._diversity = details["diversity"][i]
        chromosomes[i]._controlability = details["controlability"][i]
        chromosomes[i]._info = info[i]

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