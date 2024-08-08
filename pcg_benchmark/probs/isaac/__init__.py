from pcg_benchmark.probs.isaac.problem import IsaacProblem

PROBLEMS = {
    "isaac-v0": (IsaacProblem, {"width": 4, "height": 4}),
    "isaac-medium-v0": (IsaacProblem, {"width": 6, "height": 6}),
    "isaac-large-v0": (IsaacProblem, {"width": 8, "height": 8}),
}