from .problem import MarioProblem

PROBLEMS = {
    "smb-v0": (MarioProblem, {"width": 150}),
    "smb-medium-v0": (MarioProblem, {"width": 100}),
    "smb-small-v0": (MarioProblem, {"width": 50}),
    "smb-scene-v0": (MarioProblem, {"width": 16}),
}