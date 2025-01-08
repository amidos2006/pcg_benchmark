from pcg_benchmark.probs.sokoban.problem import SokobanProblem

PROBLEMS = {
    "sokoban-v0": (SokobanProblem, {"width": 5, "height": 5, "difficulty": 1, "solver": 5000}),
    "sokoban-complex-v0": (SokobanProblem, {"width": 5, "height": 5, "difficulty": 4, "solver": 20000}),
    "sokoban-large-v0": (SokobanProblem, {"width": 8, "height": 8, "difficulty": 3, "solver": 10000}),
}