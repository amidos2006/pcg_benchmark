<p align="center">
	<img height="300px" src="../../../images/mdungeons/example.png"/>
</p>
<h1 align="center">
MiniDungeons Problem
</h1>

This problem is based on the Mini Dungeons problem introduced by Liapis et al. in ["Procedural personas as critics for dungeon generation"](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=50c9a06c669a60491101b2e10e3887dd28c3d3f3). The game is pretty simple, the player need to reach the exit without dying. The goal of the problem is to generate a level that is fully connected and forces the player to kill enemies before reaching the exit.

The problem has 3 variants:
- `mdungeons-v0`: generate a solvable 8x12 mini dungeon level with 8 enemies in it
- `mdungeons-enemies-v0`: generate a solvable 8x12 mini dungeon level with 16 enemies
- `mdungeons-large-v0`: generate a solvable 16x24 mini dungeon level with 16 enemies

## Content Structure
```python
[
	[5, 0, 4, 0, 1, 7, 1, 3],
	[6, 0, 4, 0, 1, 0, 0, 0],
	[6, 0, 4, 0, 7, 5, 7, 1],
	[1, 6, 1, 0, 6, 6, 6, 1],
	[1, 0, 0, 0, 0, 0, 0, 1],
	[1, 1, 6, 1, 1, 0, 0, 1],
	[7, 0, 1, 0, 1, 0, 0, 1],
	[4, 0, 1, 0, 1, 1, 1, 1],
	[4, 0, 1, 0, 0, 0, 0, 0],
	[4, 0, 6, 0, 4, 5, 5, 5],
	[0, 0, 1, 0, 0, 0, 0, 1],
	[2, 1, 1, 6, 1, 7, 1, 6],
]
```

## Control Parameter


## Adding a new Variant


## Quality Measurement


## Diversity Measurement


## Controlability Measurement
