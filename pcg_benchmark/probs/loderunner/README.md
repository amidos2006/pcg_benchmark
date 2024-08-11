<p align="center">
	<img height="300px" src="../../../images/loderunner/example.png"/>
</p>
<h1 align="center">
Lode Runner Problem
</h1>

The problem has 3 variants:
- `loderunner-v0`: generate a full lode runner level of size 32x21 excluding the bottom solid floor where it has at least 6 golds and 3 enemies
- `loderunner-gold-v0`: generate a full lode runner level of size 32x21 excluding the bottom solid floor where it has at least 18 golds and 3 enemies
- `loderunner-enemies-v0`: generate a full lode runner level of size 32x21 excluding the bottom solid floor where it has at least 6 golds and 12 enemies

## Content Structure
```python
[
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,4,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,6,6,6,6,6,6,6,6,6,6,6,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,0,0,5,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,4,1,0,0,5,1,1,1,1,1,1,3,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,0,0,5,1,1,1,0,0,0,0,0,5,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,0,0,5,1,1,1,1,1,1,1,1,5,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,0,0,5,1,1,1,1,1,1,1,1,5,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,0,0,5,1,1,1,1,1,1,1,3,5,1,1,1,1],
    [0,0,0,5,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0],
    [1,1,1,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1],
    [1,1,1,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1],
    [1,1,1,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,5,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1,1,1,5,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,4,1,3,1,5,6,6,6,6,6,6,6,6,6,5,1,1,3,1,4,1,1],
    [1,1,1,1,1,1,5,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,5],
    [1,1,1,1,1,1,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,5],
    [1,1,1,1,1,1,5,1,1,1,1,1,1,1,1,1,1,2,1,1,3,1,1,1,1,1,1,1,1,1,1,5]
]
```

## Control Parameter
```python
{
    "ladder": 20,
    "rope": 30
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/loderunner/__init__.py) file. To add new variant please try to follow the following name structure `loderunner-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `width(int)`: the width of the level layout
- `height(int)`: the height of the level layout
- `gold(int)`: the minimum number of gold that should exists in the level
- `enemies(int)`: the minimum number of enemies that should exists in the level
- `exploration(float)`: the percentage of the level that is reachable by walking in the level (optional=0.4)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.6)

## Quality Measurement


## Diversity Measurement


## Controlability Measurement


## Content Info
This is all the info that you can get about any content using the `info` function:
- `player`:
- `gold`:
- `enemy`:
- `ladder`:
- `rope`:
- `exploration`:
- `collected_gold`:
- `used_tiles`:
- `tiles`:
- `walking`:
- `hanging`:
- `climbing`:
- `falling`: