from pcg_benchmark.probs.zelda.problem import ZeldaProblem

PROBLEMS = {
    "zelda-v0": (ZeldaProblem, {"width": 11, "height": 7, "enemies": 3}),
    "zelda-enemies-v0": (ZeldaProblem, {"width": 11, "height": 7, "enemies": 12}),
    "zelda-large-v0": (ZeldaProblem, {"width": 18, "height": 12, "enemies": 8}),
}