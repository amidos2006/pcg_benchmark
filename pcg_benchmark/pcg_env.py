import numpy as np

def _recursiveDiversity(structureContent):
    if len(structureContent) == 0:
        return
    structureContent = sorted(structureContent, key=lambda v: v["similar"], reverse=True)
    if structureContent[0]["similar"] <= 0:
        structureContent[0]["similar"] = 0
        return
    for sc,div in structureContent[0]["diversity"]:
        if sc == None:
            break
        if sc in structureContent:
            if div < structureContent[0]["minimum"]:
                structureContent[0]["minimum"] = div
            sc["similar"] -= 1
    _recursiveDiversity(structureContent[1:])

"""
PCG Environment class. This class is the base class where the user is interacting with.
Please don't construct this class by hand but instead use the make function from pcg_benchmark.
For example, the following code creates the environment class for the zelda-v0 problem.

import pcg_benchmark

env = pcg_benchmark.make('zelda-v0')
"""
class PCGEnv:
    """
    Parameters:
        name(str): the string name that defines the current problem
        problem(Problem): a subclass of Problem that need to be solved
    """
    def __init__(self, name, problem):
        self._name = name
        self._problem = problem

    """
    Content space property to check range or sample

    Returns:
        Space: the space of all the possible content
    """
    @property
    def content_space(self):
        return self._problem._content_space
    
    """
    Control parameter space property to check range or sample

    Returns:
        Space: the space of all the possible control parameters
    """
    @property
    def control_space(self):
        return self._problem._control_space
    
    """
    Adjust the seed of the random number generator used by the problem spaces

    Parameters:
        seed(int): the seed for the random number generator used by the problem
    """
    def seed(self, seed):
        self._problem._random = np.random.default_rng(seed)
        if(self.content_space == None):
            raise AttributeError("self._content_space is not initialized")
        self.content_space.seed(seed)
        if(self.control_space == None):
            raise AttributeError("self._control_space is not initialized")
        self.control_space.seed(seed)
    
    """
    Calculate some basic information about the contents. These information can be used to speed quality,
    diversity, and controlability calculations. You can send this to any of the other functions (quality, 
    diversity, controlability) and they will immedietly return the results as all the information are
    precomputed. 

    Parameters:
        contents(any|any[]): a single or an array of content that need to be analyzed

    Returns:
        any|any[]: a single or an array of information that can be cached to speed quality, diversity, 
        controlability calculations.
    """
    def info(self, contents):
        is_array = hasattr(contents, "__len__") and not isinstance(contents, dict)
        if is_array:
            is_content = self._problem._content_space.isSampled(contents[0])
        else:
            is_content = self._problem._content_space.isSampled(contents)
            contents = [contents]
        if not is_content:
            raise ValueError(f"")

        info = []
        for c in contents:
            info.append(self._problem.info(c))
        
        if not is_array:
            info[0]
        return info
        
    """
    Calculate the quality of the contents provided for the current problem

    Parameters:
        contents(any|any[]): a single or an array of contents or infos that need to be evaluated for quality

    Returns:
        float: percentage of passed content
        float[]: an array of the quality of each content between 0 and 1
        any[]: an array of the info of all the contents that can be cached to speed all the calculations
    """
    def quality(self, contents):
        is_array = hasattr(contents, "__len__") and not isinstance(contents, dict)
        if is_array:
            is_content = self._problem._content_space.isSampled(contents[0])
        else:
            is_content = self._problem._content_space.isSampled(contents)
            contents = [contents]
        
        infos = []
        if is_content:
            infos = self.info(contents)
        else:
            infos = contents

        quality = []
        for i in infos:
            quality.append(self._problem.quality(i))
        quality = np.array(quality)

        if not is_array:
            return float(quality[0] >= 1), quality[0], infos[0]
        return (quality >= 1).sum() / len(infos), quality, infos

    """
    Calculate the diversity of the contents provided for the current problem

    Parameters:
        contents(any|any[]): a single or an array of contents or infos that need to be evaluated for diversity

    Returns:
        float: percentage of passed content
        float[]: an array of the diversity values for each content between 0 and 1
        any[]: an array of the info of all the contents that can be cached to speed all the calculations
    """
    def diversity(self, contents):
        is_array = hasattr(contents, "__len__") and not isinstance(contents, dict)
        if is_array:
            is_content = self._problem._content_space.isSampled(contents[0])
        else:
            is_content = self._problem._content_space.isSampled(contents)
            contents = [contents]

        infos = []
        if is_content:
            infos = self.info(contents)
        else:
            infos = contents
        
        temp = []
        for i in range(len(infos)):
            temp.append({
                "index": i,
                "diversity": [],
                "similar": 0,
                "minimum": 1.0,
                "wrong": False
            })

        for i1 in range(len(temp)):
            if temp[i1]["wrong"]:
                continue
            for i2 in range(i1+1, len(temp)):
                value = self._problem.diversity(infos[i1], infos[i2])
                temp[i1]["diversity"].append((temp[i2], value))
                temp[i2]["diversity"].append((temp[i1], value))
                if value < 1:
                    temp[i1]["similar"] += 1
                    temp[i2]["similar"] += 1
        _recursiveDiversity(temp)
        temp = sorted(temp, key=lambda v: v["index"])
        diversity = []
        for sc in temp:
            diversity.append(sc["minimum"])
        diversity = np.array(diversity)

        if not is_array:
            return float(diversity[0] >= 1), diversity[0], infos[0]
        return (diversity >= 1).sum() / len(infos), diversity, infos

    """
    Calculate the controlability of the provided contents with respect to the provided controls 
    for the current problem

    Parameters:
        contents(any|any[]): a single or an array of contents or infos that need to be evaluated for controlability
        controls(any|any[]): a single or an array of controls that is used to evaluate the control of the contents

    Returns:
        float: percentage of passed content, 
        float[]: an array of the controlability values for each content between 0 and 1
        any[]: an array of the info of all the contents that can be cached to speed all the calculations
    """
    def controlability(self, contents, controls):
        is_array = hasattr(contents, "__len__") and not isinstance(contents, dict)
        if is_array:
            is_content = self._problem._content_space.isSampled(contents[0])
        else:
            is_content = self._problem._content_space.isSampled(contents)
            contents = [contents]
            controls = [controls]

        infos = []
        if is_content:
            infos = self.info(contents)
        else:
            infos = contents
        if len(infos) != len(controls):
            raise ValueError(f"Length of contents ({len(infos)}) is not equal to length of controls ({len(controls)})")
        
        controlability = []
        for i, ct in zip(infos, controls):
            controlability.append(self._problem.controlability(i, ct))
        controlability = np.array(controlability)
        
        if not is_array:
            return float(controlability[0] >= 1), controlability[0], infos[0]
        return (controlability >= 1).sum() / len(infos), controlability, infos
    
    """
    Evaluate the input contets and controls for quality, diversity, and controlability for the current problem

    Parameters:
        contents(any|any[]): a single or an array of contents or infos that need to be evaluated
        controls(any|any[]): a single or an array of controls that is used to evaluate the control of the contents

    Returns:
        float: percentage of quality passed content
        float: percentage of diversity passed content
        float: percentage of controlability passed content 
        dict[str,float[]]: a dictionary of float arrays that contains the details for quality, diversity, and controlability 
        any[]: an array of the info of all the contents that can be cached to speed all the calculations
    """
    def evaluate(self, contents, controls):
        infos = self.info(contents)
        q_score, quality, _ = self.quality(infos)
        d_score, diversity, _ = self.diversity(infos)
        ct_score, controlability, _ = self.controlability(infos, controls)

        return q_score, d_score, ct_score, {
            "quality": quality, 
            "diversity": diversity, 
            "controlability": controlability
        }, infos
    
    """
    Generate an PIL.Image for each of the content

    Parameters:
        contents(any|any[]): a single or an array of the content that need to be rendered

    Returns:
        Image|Image[]: a PIL.Image for each of the input content
    """
    def render(self, contents):
        single_input = False
        if self._problem._content_space.isSampled(contents):
            contents = [contents]
            single_input = True

        result = []
        for c in contents:
            result.append(self._problem.render(c))
        
        if single_input:
            return result[0]
        return result
