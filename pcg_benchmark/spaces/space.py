import numpy as np

class Space:
    def __init__(self):
        self._random = np.random.default_rng()
    
    def seed(self, seed):
        self._random = np.random.default_rng(seed)

    def range(self):
        return {"min": 0, "max": 0}
    
    def isSampled(self, value):
        raise NotImplementedError("Implement how to check if the input value is sampled from this space")

    def sample(self):
        raise NotImplementedError("Implement how to sample from the current space")