from pcg_benchmark.probs.loderunnertile.problem import LodeRunnerProblem

PROBLEMS = {
    "loderunnertile-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 6, "enemies": 3}),
    "loderunnertile-gold-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 18, "enemies": 3}),
    "loderunnertile-enemies-v0": (LodeRunnerProblem, {"width": 32, "height": 21, "gold": 6, "enemies": 12}),
}