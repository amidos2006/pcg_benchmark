import numpy as np

"""
A parent class that coverns the content shape and range. It can be used to sample a random content.
"""
class Space:
    """
    Constructor for the space class. It initialize the random generator.
    """
    def __init__(self):
        self._random = np.random.default_rng()
    
    """
    Adjust the seed for the random generator

    Parameters:
        seed (int): the seed value for the used random generator
    """
    def seed(self, seed):
        self._random = np.random.default_rng(seed)

    """
    Get the allowed range of the space

    Returns:
        dict[str,any]: the range of the values in space where "min" is the minimum 
        allowed value, "max" is the maximum allowed value without inclusion
    """
    def range(self):
        return {"min": 0, "max": 0}
    
    """
    Check if value is sampled from this space

    Parameters:
        value (any): an object that you want to test if it is sampled from this space

    Returns:
        bool: true if the input parameter is sampled from this space and false otherwise
    """
    def isSampled(self, value):
        raise NotImplementedError("Implement how to check if the input value is sampled from this space")

    """
    Sample an object from this space

    Returns:
        any: a sampled object from this space according to the rules of the space
    """
    def sample(self):
        raise NotImplementedError("Implement how to sample from the current space")