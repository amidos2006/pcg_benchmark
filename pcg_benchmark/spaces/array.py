from pcg_benchmark.spaces.generic import GenericSpace
from pcg_benchmark.spaces.space import Space

def _generateGenericSpace(dims, value):
    result = []
    new_dims = dims[1:]
    for _ in range(dims[0]):
        if len(new_dims) > 0:
            result.append(_generateGenericSpace(new_dims, value))
        else:
            result.append(value)
    return result

def _getInternalSpace(value):
    if hasattr(value, "__len__"):
        return _getInternalSpace(value[0])
    return value.range()

"""
An Array space that confines the content generated to be a multidimension array where each 
value in the array follow a specific space.
"""
class ArraySpace(GenericSpace):
    """
    The constructor of the Array space. 

    Parameters:
        dimensions(int[]|tuple(int)): is an array or tuple that define the shape of the array.
        value(any): a space that is used to sample every unit of the array
    """
    def __init__(self, dimensions, value):
        if not issubclass(type(value), Space):
            raise TypeError("value has to be subclass of Space class")
        if not hasattr(dimensions, "__len__"):
            dimensions = [dimensions]

        GenericSpace.__init__(self, _generateGenericSpace(dimensions, value))

    """
    Get the allowed range of the interal space of the Array space

    Returns:
        any: the range of the internal space
    """
    def range(self):
        return _getInternalSpace(self._value)