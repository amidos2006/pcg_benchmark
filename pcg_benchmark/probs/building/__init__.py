from pcg_benchmark.probs.building.problem import BuildingProblem

PROBLEMS = {
    "building-v0": (BuildingProblem, {"width": 6, "length": 6, "height": 12}),
    "building-large-v0": (BuildingProblem, {"width": 12, "length": 12, "height": 12}),
    "building-tall-v0": (BuildingProblem, {"width": 6, "length": 6, "height": 24}),
    "building-huge-v0": (BuildingProblem, {"width": 12, "length": 12, "height": 24}),
}