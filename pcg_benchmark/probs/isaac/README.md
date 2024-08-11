<style>
    img {
        image-rendering: pixelated;
    }
</style>
<p align="center">
	<img height="300px" src="../../../images/isaac/example.png"/>
</p>
<h1 align="center">
The Binding of Isaac Problem
</h1>

The problem has 3 variants:
- `isaac-v0`: generate a dungeon of size 4x4 with maximum number of rooms equal to 6
- `isaac-medium-v0`: generate a dungeon of size 6x6 with maximum number of rooms equal to 12
- `isaac-large-v0`: generate a dungeon of size 8x8 with maximum number of rooms equal to 24

## Content Structure

```python
{
    "layout": [0, 8, 12, 9, 0, 14, 11, 10, 4, 15, 7, 3, 0, 2, 0, 0],
    "start": 6,
    "boss": 8,
    "shop": 13,
    "treasure": 1,
}
```

## Control Parameter

```python
{
    "map_size": 40
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/isaac/__init__.py) file. To add new variant please try to follow the following name structure `isaac-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `width(int)`: the width of the dungeon layout
- `height(int)`: the height of the dungeon layout
- `map_size(int)`: the minimum number of rooms the dungeon should have (optional=6)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.6)

## Quality Measurement


## Diversity Measurement


## Controlability Measurement
