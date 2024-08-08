from pcg_benchmark.probs.loderunner.problem import LodeRunnerProblem

PROBLEMS = {
    "loderunner-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 6, "enemies": 3}),
    "loderunner-gold-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 18, "enemies": 3}),
    "loderunner-enemies-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 8, "enemies": 9}),
}