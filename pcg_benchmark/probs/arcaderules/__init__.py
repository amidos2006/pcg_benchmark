from pcg_benchmark.probs.arcaderules.problem import ArcadeRulesProblem

PROBLEMS = {
    # arcade rules problem with small width and height
    "arcade-v0": (ArcadeRulesProblem, {"width": 7, "height": 7}),
    # arcade rules problem with width bigger than height
    "arcade-wide-v0": (ArcadeRulesProblem, {"width": 15, "height": 7}),
    # arcade rules problem with big width and height
    "arcade-large-v0": (ArcadeRulesProblem, {"width": 15, "height": 15}),
}