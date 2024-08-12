from pcg_benchmark.probs.mdungeons.problem import MiniDungeonProblem

PROBLEMS = {
    "mdungeons-v0": (MiniDungeonProblem, {"width": 8, "height": 12, "enemies": 8}),
    "mdungeons-enemies-v0": (MiniDungeonProblem, {"width": 8, "height": 12, "enemies": 16}),
    "mdungeons-large-v0": (MiniDungeonProblem, {"width": 16, "height": 24, "enemies": 16, "solver": 10000}),
}