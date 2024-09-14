import numpy as np

class Generator:
    def __init__(self, env):
        self._env = env
        self._random = np.random.default_rng()

    def reset(self, **kwargs):
        if kwargs.get('seed'):
            self._random = np.random.default_rng(kwargs.get('seed'))

    def update(self):
        return NotImplementedError("The update function is not implemented, please make sure to implment it.")
    
    def best(self):
        return NotImplemented("The best function returns the current state of the generation (content).")
    
    def save(self, folderpath):
        raise NotImplementedError("The save function is not implemented, please make sure to implment it.")
    
    def load(self, folderpath):
        return NotImplementedError("The load function is not implemented, please make sure to implment it.")