from pcg_benchmark.probs.talakat.problem import TalakatProblem

PROBLEMS = {
    "talakat-v0": (TalakatProblem, {"width": 200, "height": 300, "spawnerComplexity": 10, "maxHealth": 150}),
    "talakat-simple-v0": (TalakatProblem, {"width": 200, "height": 300, "spawnerComplexity": 5, "min_bullets": 10, "coverage": 0.5, "maxHealth": 150}),
    "talakat-complex-v0": (TalakatProblem, {"width": 200, "height": 300, "spawnerComplexity": 20, "min_bullets": 50, "maxHealth": 150}),
    "talakat-long-v0": (TalakatProblem, {"width": 200, "height": 300, "spawnerComplexity": 20, "maxHealth": 300}),
}