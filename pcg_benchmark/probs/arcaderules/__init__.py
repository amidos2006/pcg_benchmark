from pcg_benchmark.probs.arcaderules.problem import ArcadeRulesProblem

PROBLEMS = {
    "arcade-v0": (ArcadeRulesProblem, {"width": 7, "height": 7}),
    "arcade-wide-v0": (ArcadeRulesProblem, {"width": 15, "height": 7}),
    "arcade-large-v0": (ArcadeRulesProblem, {"width": 15, "height": 15}),
}