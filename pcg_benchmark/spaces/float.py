from pcg_benchmark.spaces.space import Space

"""
An Integer space that confines the content generated from it to be an float in a specific range
"""
class FloatSpace(Space):
    """
    The constructor of the Float space. 
    There are both optional parameters if both are not provided then the range [0,1)
    If only one parameter is provided then the range is [0,min_value)
    Otherwise the range is [min_value, max_value)

    Parameters:
        min_value(int): the minimum value that can be sampled from the space.
        max_value(int): the maximum value that space can't exceed (excluded)
    """
    def __init__(self, min_value = None, max_value = None):
        Space.__init__(self)

        if min_value == None and max_value == None:
            min_value = 0
            max_value = 1
        elif max_value == None:
            max_value = min_value
            min_value = 0

        if min_value >= max_value:
            raise ValueError("min_value has to be smaller than max_value")

        self._min_value = min_value
        self._max_value = max_value

    """
    Get the allowed range of the float space

    Returns:
        dict[str,float]: a dictionary with "min" and "max" float values where "max" value is never reached
    """
    def range(self):
        return {"min": self._min_value, "max": self._max_value}

    """
    Check if the float parameter fells in the range of the float space

    Parameters:
        value (any): a sampled content that need to be tested

    Returns:
        bool: True if the input value is float that lies in the float space range
    """
    def isSampled(self, value):
        try:
            return value >= self._min_value and value < self._max_value
        except:
            return False
    
    """
    Sample a float from the float space that falls in range

    Returns:
        float: a float that lies in the range of the float space
    """
    def sample(self):
        return self._random.random() * (self._max_value - self._min_value) + self._min_value
    
    """
    Removes a value from the array and return that as float in the space range
    
    Parameters:
        values(float[]): a group of values to restructure
        copy(bool): copy the values array before modifying it

    Returns:
        int: a correctly bounded value in the float space
    """
    def restructure(self, values, copy=True):
        if len(values) == 0:
            raise ValueError("The input values is empty.")
        if copy:
            values = [] + values
        value = float(values.pop(0))
        if value < self._min_value:
            value = self._min_value
        if value > self._max_value:
            value = self._max_value
        return value
