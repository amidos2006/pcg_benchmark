from pcg_benchmark.probs.smbtile.problem import MarioProblem

PROBLEMS = {
    "smbtile-v0": (MarioProblem, {"width": 150}),
    "smbtile-medium-v0": (MarioProblem, {"width": 100}),
    "smbtile-small-v0": (MarioProblem, {"width": 50}),
    "smbtile-scene-v0": (MarioProblem, {"width": 16}),
}