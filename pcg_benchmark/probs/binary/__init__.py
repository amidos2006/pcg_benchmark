from pcg_benchmark.probs.binary.problem import BinaryProblem

PROBLEMS = {
    "binary-v0": (BinaryProblem, {"width": 14, "height": 14}),
    "binary-wide-v0": (BinaryProblem, {"width": 28, "height": 14}),
    "binary-large-v0": (BinaryProblem, {"width": 28, "height": 28}),
}