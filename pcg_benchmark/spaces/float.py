from pcg_benchmark.spaces.space import Space

class FloatSpace(Space):
    def __init__(self, min_value = None, max_value = None):
        Space.__init__(self)

        if min_value == None and max_value == 0:
            min_value = 0
            max_value = 1
        elif max_value == None:
            max_value = min_value
            min_value = 0

        if min_value >= max_value:
            raise ValueError("min_value has to be smaller than max_value")

        self._min_value = min_value
        self._max_value = max_value

    def range(self):
        return {"min": self._min_value, "max": self._max_value}

    def isSampled(self, value):
        try:
            return value >= self._min_value and value < self._max_value
        except:
            return False
    
    def sample(self):
        return self._random.random() * (self._max_value - self._min_value) + self._min_value
