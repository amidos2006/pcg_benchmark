import numpy as np

"""
An internal recursive function to flatten the input structure into an array of floats

Parameters:
    input (any): the input structure to flatten usually something sampled from a space

Returns:
    float[]: a 1D array of floats without any structure (multidimension array, dictionary, etc.)
"""
def _recursiveFlat(input):
    if not hasattr(input, "__len__"):
        return [float(input)]
    if isinstance(input, dict):
        result = []
        for v in input:
            result = result + _recursiveFlat(input[v])
        return result
    result = []
    for v in input:
        result = result + _recursiveFlat(v)
    return result

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
    
    """
    Restructure the input values into the space structure

    Parameters:
        values(float[]): a group of values to restructure
        copy(bool): copy the values array before modifying it

    Returns:
        any: a correctly structured object of the input values
    """
    def restructure(self, values, copy=True):
        raise NotImplementedError("Implement how to structure 1D array to the current space")
    
    """
    Special sampling function where it return the content as 1D array of floats

    Returns:
        float[]: a 1D array of floats that consists of everything
    """
    def sampleFlat(self):
        return _recursiveFlat(self.sample())