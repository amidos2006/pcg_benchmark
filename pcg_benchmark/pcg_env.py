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

class PCGEnv:
    def __init__(self, name, problem):
        self._name = name
        self._problem = problem

    def seed(self, seed):
        self._problem.seed(seed)

    def parameters(self, **kwargs):
        if kwargs.get("seed", None) != None:
            self.seed(kwargs.get("seed"))
        self._problem.parameters(**kwargs)

    def random_content(self, amount=100):
        result = []
        for _ in range(amount):
            result.append(self._problem.random_content())
        return result
    
    def random_control(self, amount=100):
        result = []
        for _ in range(amount):
            result.append(self._problem.random_control())
        return result
    
    def content_range(self):
        return self._problem.content_range()
    
    def control_range(self):
        return self._problem.control_range()
    
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
