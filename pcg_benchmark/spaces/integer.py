from pcg_benchmark.spaces.space import Space

class IntegerSpace(Space):
    def __init__(self, min_value = None, max_value = None):
        Space.__init__(self)

        if min_value == None and max_value == 0:
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

    def range(self):
        return {"min": self._min_value, "max": self._max_value}

    def isSampled(self, value):
        try:
            if not value.is_integer():
                return False
            value = int(value)
            return value >= self._min_value and value < self._max_value
        except:
            return False

    def sample(self):
        return self._random.integers(self._min_value, self._max_value)