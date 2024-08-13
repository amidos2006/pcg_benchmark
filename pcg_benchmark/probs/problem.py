import numpy as np

"""
A parent class for all the problems in the benchmark
"""
class Problem:
    """
    constructor for the problem. All the children classes have to initialize the content_space
    and the control_space

    Parameters:
        kwargs(any): these are the parameters for the child problem class
    """
    def __init__(self, **kwargs):
        self._random = np.random.default_rng()
        self._content_space = None
        self._control_space = None
    
    """
    Get all the needed information about the content to be able to evaluate it fast.
    This class is called before calling quality, diversity, or controlability. 
    This function is useful to speed the process for calculating all the metrics. 
    All sub classes need to implement that function.

    Parameters:
        content(any): the content that need to be evaluated

    Returns:
        dict[str,any]: return a dictionary with all the information needed for the
        calculations of quality, diversity, and controlability
    """
    def info(self, content):
        raise NotImplementedError("info function is not implemented")

    """
    Calculate the quality of a content as a value between 0 and 1 where 1 means it passes
    the benchmark criteria. The quality function should allow for more than 1 content to
    have the value of 1 which means that the metric passes the quality criteria of the
    current problem.

    Parameters:
        info(dict[str,any]): the information about the tested content. Make sure that info function
        return all the releavant values need to calculate the quality

    Returns:
        float: return a value between 0 and 1 where 1 means the metric passes the quality
        criteria
    """
    def quality(self, info):
        raise NotImplementedError("quality function is not implemented")
    
    """
    Calculate the diversity between two content as a value between 0 and 1 where 1 means it passes
    the benchmark criteria.

    Parameters:
        info1(dict[str,any]): the information about the first content to be tested for diversity. 
        Make sure that info function return all the values need to calculate the diversity
        info2(dict[str,any]): the information about the second content to be tested for diversity. 
        Make sure that info function return all the values need to calculate the diversity

    Returns:
        float: return a value between 0 and 1 for how much these two content are different from each
        other where 1 means the metric passes the diversity criteria
    """
    def diversity(self, info1, info2):
        raise NotImplementedError("diversity function is not implemented")
    
    """
    Calculate the controlability of a content with respect to the control criteria as a value 
    between 0 and 1 where 1 means it passes the benchmark criteria. The controlability function 
    should allow for more than 1 content to have the value of 1 which means that the metric passes 
    the controlability criteria of the current problem.

    Parameters:
        info(dict[str,any]): the information about the tested content. Make sure that info function
        return all the releavant values need to calculate the controlability
        control(any): the control parameter that need to be tested.

    Returns:
        float: return a value between 0 and 1 where 1 means the metric passes the controlability
        criteria with respect to that control parameter
    """
    def controlability(self, info, control):
        raise NotImplementedError("controlability function is not implemented")
    
    """
    Render the content in a form of a PIL.Image so the user can see how it looks like

    Parameters:
        content(any): the input content that need to be rendered

    Returns:
        Image: the rendered image of the content
    """
    def render(self, content):
        raise NotImplementedError("render function is not implemented")