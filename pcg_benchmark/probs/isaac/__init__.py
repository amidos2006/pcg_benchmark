from pcg_benchmark.probs.isaac.problem import IsaacProblem

PROBLEMS = {
    "isaac-v0": (IsaacProblem, {"width": 4, "height": 4, "rooms": 6}),
    "isaac-medium-v0": (IsaacProblem, {"width": 6, "height": 6, "rooms": 12}),
    "isaac-large-v0": (IsaacProblem, {"width": 8, "height": 8, "rooms": 24}),
}