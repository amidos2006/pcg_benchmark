from pcg_benchmark.spaces.float import FloatSpace
from pcg_benchmark.spaces.integer import IntegerSpace
from pcg_benchmark.spaces.array import ArraySpace
from pcg_benchmark.spaces.generic import GenericSpace
from pcg_benchmark.spaces.dictionary import DictionarySpace

def isContentEqual(content1, content2):
    try:
        if not hasattr(content1, "__len__"):
            return content1 == content2
        if isinstance(content1, dict):
            for v in content1:
                if not isContentEqual(content1[v], content2[v]):
                    return False
            return True
        for i in range(len(content1)):
            if not isContentEqual(content1[i], content2[i]):
                return False
        return True
    except:
        return False