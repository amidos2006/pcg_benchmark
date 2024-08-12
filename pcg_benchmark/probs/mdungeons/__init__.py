from pcg_benchmark.probs.mdungeons.problem import MiniDungeonProblem

PROBLEMS = {
    "mdungeon-v0": (MiniDungeonProblem, {"width": 8, "height": 12, "enemies": 8}),
    "mdungeon-enemies-v0": (MiniDungeonProblem, {"width": 8, "height": 12, "enemies": 16}),
    "mdungeon-large-v0": (MiniDungeonProblem, {"width": 16, "height": 24, "enemies": 16, "solver": 10000}),
}