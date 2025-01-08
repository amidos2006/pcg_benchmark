from pcg_benchmark.probs.elimination.problem import EliminationProblem

PROBLEMS = {
    "elimination-v0": (EliminationProblem, {"letters": 8, "short_percentage": 0.5, "long_percentage": 0.7}),
    "elimination-easy-v0": (EliminationProblem, {"letters": 6, "short_percentage": 0.2, "long_percentage": 0.4}),
    "elimination-hard-v0": (EliminationProblem, {"letters": 10, "short_percentage": 0.8, "long_percentage": 0.9}),
}