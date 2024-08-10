<p align="center">
	<img height="300px" src="../../../images/ddave/example.png"/>
</p>
<h1 align="center">
Dangerous Dave Problem
</h1>

This is a small discrete version of the DOS game [Dangerous Dave](https://www.retrogames.cz/play_480-DOS.php) similar to the one implemented in the [PCGRL Framework](https://github.com/amidos2006/gym-pcgrl). Dangerous dave is a small platformer where you need to get a key avoid spikes and collect diamonds and get to exit. The goal is to create a playable Dangerous Dave level where the player can get reach key, door, and diamonds. Finally, the game solution should have a minimum number of jumps.

The problem has 3 variants:
- `ddave-v0`: generate a 11x7 level where the solution has minimum number of jumps equal to 2.
- `ddave-complex-v0`: generate a 11x7 level where the solution has minim number of jumps equal to 6.
- `ddave-large-v0`: generate a 17x11 level where the solution has minimum number of jumps equal to 10.

## Content Structure
The content is a 2D array **height x width** of int of values between 0 and 6 that represents a dangeroud dave level. Here is an example of a level
```python
[
    [1,1,6,6,6,1,1,4,1,1,5],
    [1,1,1,1,1,1,1,0,0,0,0],
    [4,4,1,1,1,4,4,1,1,1,1],
    [0,0,1,1,1,0,0,1,1,1,1],
    [1,1,4,4,4,1,1,4,4,4,1],
    [1,1,0,0,0,1,1,0,0,0,1],
    [2,1,1,1,1,1,1,0,3,1,1],
]
```
Different values has different meaning
- *0:* solid tile
- *1:* empty tile
- *2:* player tile
- *3:* exit tile
- *4:* diamond tile
- *5:* key tile
- *6:* spike tile

## Control Parameter
The control parameter provides the player starting location (`sx` and `sy`), exit location (`ex` and `ey`), and finally number of diamonds that should appear in the level (`diamonds`). Here is an example of the control parameter.
```python
{
    "sx": 0,
    "sy": 6,
    "ex": 3,
    "ey": 0,
    "diamonds": 4
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/ddave/__init__.py) file. To add new variant please try to follow the following name structure `ddave-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `width(int)`: the width of the level
- `height(int)`: the height of the level
- `jumps(int)`: the minimum number of jumps that has to be in the solution
- `solver(int)`: the solver power for checking level solvability, the higher the better but also the slower (optional=5000)
- `diversity(float)`: the diversity percentage that if passes it it is 1 (optional=0.4)

## Quality Measurement
To pass the quality criteria, you need to pass multiple of criteria
- have one player, one key, and one door
- the level has to be playable and the level solution has to have the minimum number of jumps
- Finally, all the diamonds need to be reachable

## Diversity Measurement
To pass the diversity criteria, you need the solution heatmap between the two levels have at least 40% difference on the hamming distance measuring criteria.

## Controlability Measurement
To pass the controlability criteria, you need the starting and ending location of the player at certain locations and the number of reachable diamonds equal to the control parameter values.