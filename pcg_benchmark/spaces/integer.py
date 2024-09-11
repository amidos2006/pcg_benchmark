from pcg_benchmark.spaces.space import Space

"""
An Integer space that confines the content generate from it to be an integer in a specific range
"""
class IntegerSpace(Space):
    """
    The constructor of the Integer space. 
    There are both optional parameters if both are not provided then the range [0,2)
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
            max_value = 2
        elif max_value == None:
            max_value = min_value
            min_value = 0

        if not isinstance(min_value, int):
            raise TypeError("min_value should be an integer value")
        if not isinstance(max_value, int):
            raise TypeError("max_value should be an integer value")

        if min_value >= max_value:
            raise ValueError("min_value has to be smaller than max_value")
        
        self._min_value = min_value
        self._max_value = max_value

    """
    Get the allowed range of the integer space

    Returns:
        dict[str,int]: a dictionary with "min" and "max" integer values where "max" value is excluded
    """
    def range(self):
        return {"min": self._min_value, "max": self._max_value}

    """
    Check if the integer parameter fells in the range of the integer space

    Parameters:
        value (any): a sampled content that need to be tested

    Returns:
        bool: True if the input value is integer that lies in the integer space range
    """
    def isSampled(self, value):
        try:
            value = int(value)
            return value >= self._min_value and value < self._max_value
        except:
            return False

    """
    Sample an integer from the integer space that falls in range

    Returns:
        int: an integer that lies in the range of the integer space
    """
    def sample(self):
        return self._random.integers(self._min_value, self._max_value)
    

    """
    Removes a value from the array and return that as integer in the space range

    Parameters:
        values(float[]): a group of values to restructure
        copy(bool): copy the values array before modifying it

    Returns:
        int: a correctly bounded value in the integer space
    """
    def restructure(self, values, copy=True):
        if len(values) == 0:
            raise ValueError("The input values is empty.")
        if copy:
            values = [] + values
        value = int(values.pop(0))
        if value < self._min_value:
            value = self._min_value
        if value > self._max_value:
            value = self._max_value
        return value
        