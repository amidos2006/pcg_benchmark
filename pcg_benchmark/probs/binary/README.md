<p align="center">
	<img height="300px" src="../../../images/binary/example.png"/>
</p>
<h1 align="center">
Binary Problem
</h1>

The binary problem is from the [PCGRL framework](https://github.com/amidos2006/gym-pcgrl) where the goal is to generate a 2D maze of empty and solid tile where it is fully connected and have a long path in it that is more than the a specific distance. The default value is equal to the width + height of the map.

The problem has 3 variants:
- `binary-v0`: generate a maze of size 14x14 (excluding borders) with minimum path length of 28
- `binary-wide-v0`: generate a maze of size 28x14 (excluding borders) with minimum path length of 42
- `binary-large-v0`: generate a maze of size 28x28 (excluding borders) with minimum path length of 56

## Content Structure
The content is a 2D binary array of **height x width** where 1 is **empty** and 0 is **solid**. Here is an example of a content
```python
[
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,0,1,1,1],
    [1,1,1,0,0,0,0,1,1,1,0,1,1,1],
    [1,1,1,0,1,1,1,1,1,1,0,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,1,1,1],
    [1,1,1,1,1,1,1,0,1,1,1,1,1,1],
    [0,0,0,0,1,1,1,0,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,0,1,1,1,0,1,1],
    [0,1,1,1,1,1,1,0,1,1,1,0,0,0],
    [0,1,1,0,1,1,1,0,1,1,1,1,1,1],
    [0,1,1,0,0,0,0,0,0,0,0,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,0,1,1,1],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
```

## Control Parameter
This is the control parameter of the problem. The control parameter is dictionary with one parameter called `path(int)` where it indicates how long the shortest longest path have to be to pass controlability criteria. Here is an example of the control parameter for 14x14:
```python
{
    "path": 50
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/binary/__init__.py) file. To add new variant please try to follow the following name structure `binary-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `width(int)`: the width of the maze
- `height(int)`: the height of the maze
- `path(float)`: the target path length (optional=width+height)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.4) 

An easier way without editing the framework files is to use the `register` function from the `pcg_benchmark` to add the variant.
```python
from pcg_benchmark.probs.binary import BinaryProblem
import pcg_benchmark

pcg_benchmark.register('binary-extreme-v0', BinaryProblem, {"width": 50, "length": 50, "path": 500})
```

## Quality Measurement
To pass the quality criteria, you need to pass two of criteria
- have a fully connected map that consists of one region
- have a longest shortest path length that is more than the target `path` which is 28 for `binary-v0`

## Diversity Measurement
To pass the diversity criteria, you need the input levels have at least 40% difference on the hamming distance measuring criteria.

## Controlability Measurement
To pass the controlability criteria, you need the path length (the longest shortest path) close to the control parameter `path` value.

## Content Info
This is all the info that you can get about any content using the `info` function:
- `path(int)`: the value longest shortest path in the maze 
- `regions(int)`: the number of connected empty regions in the maze
- `flat(int[])`: the maze as a flat 1D binary array