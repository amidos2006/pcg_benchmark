from pcg_benchmark.spaces.space import Space

"""
Seed all the random number generators in all the spaces inside each other

Parameter:
    input(Space): a space subclass that need to be seeded
    seed(int): the seed for the random number generator
"""
def _recursiveSeed(input, seed):
    if not hasattr(input, "__len__"):
        if issubclass(type(input), Space):
            input.seed(seed)
    else:
        for v in input:
            if isinstance(input, dict):
                _recursiveSeed(input[v], seed)
            else:
                _recursiveSeed(v, seed)

"""
Sample a value from space recursively

Parameters:
    input(Space): a space subclass need to be sampled

Returns:
    any: a sampled content from the input space
"""
def _recursiveSample(input):
    if not hasattr(input, "__len__"):
        if issubclass(type(input), Space):
            return input.sample()
        else:
            return input
    if isinstance(input, dict):
        result = {}
        for v in input:
            result[v] = _recursiveSample(input[v])
        return result
    result = []
    for v in input:
        result.append(_recursiveSample(v))
    return result

"""
Get the range of a space recursively

Parameters:
    input(Space): a space subclass need to get its range

Returns:
    dict[str,any]: a dictionary of the range values needed from the input space
"""
def _recursiveRange(input):
    if not hasattr(input, "__len__"):
        if issubclass(type(input), Space):
            return input.range()
        else:
            return { "min": input, "max": input }
    if isinstance(input, dict):
        result = {}
        for v in input:
            result[v] = _recursiveRange(input[v])
        return result
    result = []
    for v in input:
        result.append(_recursiveRange(v))
    return result

"""
Check recursively if the sampled value is from a specific space

Parameters:
    input(Space): a space subclass used to check if the value is sampled from
    value(any): a value that need to checked if it was from input space

Returns:
    bool: True if the value is sampled from the input space and False otherwise
"""
def _recursiveIsSampled(input, value):
    try:
        if not hasattr(input, "__len__"):
            if issubclass(type(input), Space):
                return input.isSampled(value)
            else:
                return input == value
        if isinstance(input, dict):
            for v in input:
                if not _recursiveIsSampled(input[v], value[v]):
                    return False
            return True
        for i in range(len(input)):
            if not _recursiveIsSampled(input[i], value[i]):
                return False
        return True
    except:
        return False
    
"""
Restructure recursively the value into same shape of input

Parameters:
    input(Space): a space subclass used to use to restructure the input value
    value(any): a value that need to be restructured into the shape of the input

Returns:
    any: a structured object in same vein of input but using values from the value parameter
"""
def _recursiveRestructure(input, value):
    if not hasattr(input, "__len__"):
        if issubclass(type(input), Space):
            return input.restructure(value, False)
        else:
            if len(value) == 0:
                raise ValueError("The input values is empty.")
            value.pop(0)
            return input
    if isinstance(input, dict):
        result = {}
        for v in input:
            result[v] = _recursiveRestructure(input[v], value)
        return result
    result = []
    for i in range(len(input)):
        result.append(_recursiveRestructure(input[i], value))
    return result

"""
This space return what is inside of it as it is and sample from it if it is space. 
This is used for any structure of data like arrays and dictionary mixed with constant values.
For example: You can have an array of float or integer or dictionary then Discrete Space.
"""
class GenericSpace(Space):
    """
    The constructor of the space

    Parameters:
        value (Any): this can be anything such as string, number, array, or dictionary
    """
    def __init__(self, value = None):
        Space.__init__(self)

        if value == None:
            value = 1
        self._value = value

    """
    Get the allowed range recursively for the generic space

    Returns:
        any: a recursive range of the used spaces where each one will have "min" and "max" values
    """
    def range(self):
        return _recursiveRange(self._value)

    """
    Adjust the seed for the random generator for all the spaces

    Parameters:
        seed (int): the seed value for the used random generator
    """
    def seed(self, seed):
        _recursiveSeed(self._value, seed)
    
    """
    Check if the parameter is sampled from that space recursively

    Parameters:
        value (any): a sampled content that need to be tested

    Returns:
        bool: True if the parameter is sampled from this space
    """
    def isSampled(self, value):
        return _recursiveIsSampled(self._value, value)

    """
    Sample a content from this space recursively

    Returns:
        any: a sampled content from the space that follow the same data structure
    """
    def sample(self):
        return _recursiveSample(self._value)
    
    """
    Removes values from the array and returns the value in the generic structure
    
    Parameters:
        values(float[]): a group of values to restructure
        copy(bool): copy the values array before modifying it

    Returns:
        any: a correctly bounded value in the generic space
    """
    def restructure(self, values, copy=True):
        if copy:
            values = [] + values
        return _recursiveRestructure(self._value, values)
