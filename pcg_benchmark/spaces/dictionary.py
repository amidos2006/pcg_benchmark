from pcg_benchmark.spaces.generic import GenericSpace

"""
A Dictionary space that confines the content generated to be a dictionary where it has the same keys 
as the input and each value is sampled from the space of each of these keys.
"""
class DictionarySpace(GenericSpace):
    """
    The constructor of the Dictionary space. 

    Parameters:
        dictionary(dict[str,any]): is a dictionary of strings with spaces for each key.
    """
    def __init__(self, dictionary):
        for key in dictionary:
            if not isinstance(key, str):
                raise TypeError("dictionary keys has to be string")
        GenericSpace.__init__(self, dictionary)
