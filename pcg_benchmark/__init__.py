from .pcg_env import PCGEnv
from .probs import PROBLEMS
from difflib import SequenceMatcher

"""
Register a new problem that is not part of the probs folder to the system

Parameters:
    name (string): the name of the problem, usually the basic name is {name}-{version} 
    for example zelda-v0 for a modified version of the problem it follows {name}-{modification}-{version} 
    for example zelda-enemies-v0.
    problemClass (class): the class of the problem and it has to be a subclass of pcg_benchmark.probs.problem.Problem.
    problemArgs (dict[string,any]): the parameters the constructor of the problemClass needs for example 
    width and height for level generation.
"""
def register(name, problemClass, **problemArgs):
    if name in PROBLEMS:
        raise AttributeError(f'This problem name ({name}) is already been defined')
    PROBLEMS[name] = (problemClass, problemArgs)

"""
Get all the registered environments in the pcg_benchmark either using register function or 
from exisiting in probs folder.

Returns:
    string[]: an array of all the names of the registered environments in pcg_benchmark.
"""
def list():
    names = []
    for name in PROBLEMS:
       names.append(name)
    return names

"""
create and initialize an environment from the pcg_benchmark using its name.

Parameters:
    name (string): the name of the environment that you want to initialize.

Returns:
    PCGEnv: an environment of that problem where you can test quality, diversity, 
    and controllability of your generator.
"""
def make(name):
    if not (name in PROBLEMS):
        prob_names = PROBLEMS.keys()
        max_sim = 0
        sim_name = ""
        for n in prob_names:
            sim = SequenceMatcher(None, n, name).ratio()
            if sim > max_sim:
                max_sim = sim
                sim_name = n
        raise NotImplementedError(f'This problem ({name}) is not implemented. Did you mean to write ({sim_name}) instead.')
    problemClass = PROBLEMS[name]
    problemArgs = {}
    if hasattr(PROBLEMS[name], "__len__"):
        problemClass = PROBLEMS[name][0]
        if len(PROBLEMS[name]) > 1:
            problemArgs = PROBLEMS[name][1]
    return PCGEnv(name, problemClass(**problemArgs))