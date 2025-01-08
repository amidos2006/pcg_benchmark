from pcg_benchmark.spaces.float import FloatSpace
from pcg_benchmark.spaces.integer import IntegerSpace
from pcg_benchmark.spaces.array import ArraySpace
from pcg_benchmark.spaces.generic import GenericSpace
from pcg_benchmark.spaces.dictionary import DictionarySpace
import copy
import numpy as np

"""
Check if the two input content are equal

Parameters:
    content1 (any): content from a space
    content2 (any): content from a space

Returns:
    bool: return if content1 and content 2 are equal in all the values
"""
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

"""
An internal recursive function to swap two contents together based on specific probability and 
maximum number of swaps

Parameters:
    content1 (any): content from a space
    content2 (any): content from a space
    swapInfo (dict): dictionary containing the maximum number of swaps and the probability of 
    swapping and any additional information for later

Returns:
    any: returns the swapped content
"""
def _recursiveSwap(content1, content2, swapInfo):
    if not hasattr(content1, "__len__"):
        if swapInfo["maxSwaps"] != 0 and swapInfo["random"].random() < swapInfo["probability"]:
            swapInfo["maxSwaps"] -= 1
            return copy.deepcopy(content2)
        return copy.deepcopy(content1)
    if isinstance(content1, dict):
        result = {}
        for v in content1:
            result[v] = _recursiveSwap(content1[v], content2[v], swapInfo)
        return result
    result = []
    for c1,c2 in zip(content1, content2):
        result.append(_recursiveSwap(c1, c2, swapInfo))
    return result

"""
Swap the two provided content with a given probability where each element of the content has 
the same probability to be swapped with the other content and have maximum number of swaps

Parameters:
    content1 (any): content from a space
    content2 (any): content from a space
    swap_probability (float): probability of swapping each part of the content
    maxSwaps (int): maximum number of swaps allowed
    seed (any): seed for the random number generator or the random number generator itself

Returns:
    any: returns the swapped content
"""
def contentSwap(content1, content2, swap_probability, maxSwaps=-1, seed = None):
    if seed == None:
        random = np.random.default_rng()
    elif isinstance(seed, np.random.Generator):
        random = seed
    else:
        random = np.random.default_rng(seed)
    swapInfo = {
        "maxSwaps": maxSwaps,
        "probability": swap_probability,
        "random": random
    }
    return _recursiveSwap(content1, content2, swapInfo)

    