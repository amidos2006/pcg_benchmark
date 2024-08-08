from pcg_benchmark.spaces.space import Space

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

    def range(self):
        return _recursiveRange(self._value)

    def seed(self, seed):
        _recursiveSeed(self._value, seed)
    
    def isSampled(self, value):
        return _recursiveIsSampled(self._value, value)

    def sample(self):
        return _recursiveSample(self._value)
