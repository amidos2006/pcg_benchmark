import numpy as np
from pcg_benchmark.spaces import isContentEqual

class Problem:
    def __init__(self, **kwargs):
        self._random = np.random.default_rng()
        self._content_space = None
        self._control_space = None
    
    def seed(self, seed):
        self._random = np.random.default_rng(seed)
        if(self._content_space == None):
            raise AttributeError("self._content_space is not initialized")
        self._content_space.seed(seed)
        if(self._control_space == None):
            raise AttributeError("self._control_space is not initialized")
        self._control_space.seed(seed)

    def parameters(self, **kwargs):
        return
    
    def random_content(self):
        if(self._control_space == None):
            raise AttributeError("self._content_space is not initialized")
        return self._content_space.sample()
    
    def random_control(self):
        if(self._control_space == None):
            raise AttributeError("self._control_space is not initialized")
        return self._control_space.sample()
    
    def content_range(self):
        if(self._control_space == None):
            raise AttributeError("self._content_space is not initialized")
        return self._content_space.range()
    
    def control_range(self):
        if(self._control_space == None):
            raise AttributeError("self._control_space is not initialized")
        return self._control_space.range()
    
    def info(self, content):
        raise NotImplementedError("info function is not implemented")

    def quality(self, info):
        raise NotImplementedError("quality function is not implemented")
    
    def diversity(self, info1, info2):
        raise NotImplementedError("diversity function is not implemented")
    
    def controlability(self, info, control):
        raise NotImplementedError("controlability function is not implemented")
    
    def render(self, content):
        raise NotImplementedError("render function is not implemented")