from pcg_benchmark.probs.building.problem import BuildingProblem

PROBLEMS = {
    "building-v0": (BuildingProblem, {"width": 7, "length": 7, "height": 12, "blocks": 40}),
    "building-large-v0": (BuildingProblem, {"width": 11, "length": 11, "height": 12, "blocks": 180}),
    "building-tall-v0": (BuildingProblem, {"width": 7, "length": 7, "height": 24, "blocks": 80}),
    "building-huge-v0": (BuildingProblem, {"width": 11, "length": 11, "height": 24, "blocks": 360}),
}