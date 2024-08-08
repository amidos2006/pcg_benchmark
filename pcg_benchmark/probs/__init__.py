from pcg_benchmark.probs.problem import Problem
from importlib import import_module
import os

PROBLEMS = {   
}

folders = [f for f in os.listdir(os.path.dirname(__file__))\
            if not (f.startswith(".") or f.startswith("__")) and\
            os.path.isdir(os.path.join(os.path.dirname(__file__), f))]

for module_name in folders:
    module = import_module(f"pcg_benchmark.probs.{module_name}")
    if hasattr(module, "PROBLEMS"):
        for prob in module.PROBLEMS:
            PROBLEMS[prob] = module.PROBLEMS[prob]