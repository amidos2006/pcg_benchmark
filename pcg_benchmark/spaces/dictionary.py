from pcg_benchmark.spaces.generic import GenericSpace

class DictionarySpace(GenericSpace):
    def __init__(self, dictionary):
        for key in dictionary:
            if not isinstance(key, str):
                raise TypeError("dictionary keys has to be string")
        GenericSpace.__init__(self, dictionary)
