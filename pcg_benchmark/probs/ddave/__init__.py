from pcg_benchmark.probs.ddave.problem import DangerDaveProblem

PROBLEMS = {
    "ddave-v0": (DangerDaveProblem, {"width": 11, "height": 7, "jumps": 2}),
    "ddave-complex-v0": (DangerDaveProblem, {"width": 11, "height": 7, "jumps": 6}),
    "ddave-large-v0": (DangerDaveProblem, {"width": 17, "height": 11, "jumps": 10}),
}