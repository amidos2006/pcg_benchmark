from pcg_benchmark.probs.talakat.problem import TalakatProblem

PROBLEMS = {
    "talakat-v0": (TalakatProblem, {"width": 200, "height": 320, "spawnerComplexity": 10, "maxHealth": 150}),
    "talakat-small-v0": (TalakatProblem, {"width": 100, "height": 160, "spawnerComplexity": 5, "maxHealth": 150}),
    "talakat-long-v0": (TalakatProblem, {"width": 200, "height": 320, "spawnerComplexity": 15, "maxHealth": 300}),
}