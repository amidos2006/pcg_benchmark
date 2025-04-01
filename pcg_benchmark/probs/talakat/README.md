<p align="center">
	<img height="300px" src="../../../images/talakat/example.gif"/>
</p>
<h1 align="center">
Talakat Problem
</h1>

This framework is just generating a short bullet patterns for [Talakat framework](https://github.com/amidos2006/Talakat). This framework was introduced by Khalifa et al. in ["Talakat: Bullet Hell Generation through Constrained Map-Elites"](https://arxiv.org/abs/1806.04718). The goal is to generate a short bullet pattern sequence that cover most of the gameplay space and have on average a minimum amount of bullets.

The problem has 3 variants:
- `talakat-v0`: this is the basic problem where you need to have 20 bullets on average per frame with high coverage of the whole space for 150 frames
- `talakat-simple-v0`: a simpler version where the pattern needs to have 10 bullets on average per frame with high coverage of the whole space for 150 frames
- `talakat-complex-v0`: a more complex version where the pattern needs to have 50 bullets on average per frame with high coverage of the whole space for 150 frames
- `talakat-long-v0`: a longer version of the normal problem with longer amount frames (300 frames)

## Content Structure
The content representation is a 2D array of int where each array is a spawner and the last array is the one that get spawned. The array is a group of integer numbers between 0 and 99 that is used by [Tracery](https://tracery.io/) to expand the [Talakat grammar](https://github.com/amidos2006/Talakat/wiki/Scripting-Language) to be a script. Here is an example of a content:
```python
[
	[95, 59, 66, 31, 52, 67, 84, 32, 1, 16, 82, 98, 64, 30, 60, 57, 21, 90, 66, 76, 70, 14, 0, 20, 63, 93, 58, 73, 29, 3, 92, 39, 67, 72, 91, 73, 32, 64, 56, 35, 33, 57, 80, 6, 99, 25, 7, 72, 31, 86, 19, 92, 23, 1, 38, 46, 20, 87, 62, 85, 3, 54, 13, 98, 86, 12, 34, 45, 95, 1, 63, 11, 96, 71, 39, 79, 49, 15, 57, 80, 34, 70, 93, 14, 43, 88, 68, 11, 58, 94, 37, 52, 82, 64, 3, 17, 29, 80, 90, 90], 
	[87, 2, 98, 49, 7, 81, 76, 52, 89, 26, 80, 29, 38, 63, 71, 44, 89, 74, 8, 61, 49, 68, 48, 43, 45, 64, 26, 89, 65, 22, 61, 84, 67, 14, 23, 43, 99, 35, 74, 53, 25, 70, 20, 78, 19, 57, 83, 45, 50, 90, 96, 76, 52, 97, 13, 26, 71, 99, 62, 95, 98, 46, 83, 52, 86, 48, 17, 10, 69, 71, 23, 49, 98, 92, 50, 79, 0, 11, 65, 13, 31, 63, 68, 33, 97, 82, 13, 33, 5, 18, 51, 11, 26, 76, 16, 20, 3, 54, 95, 2], 
	[85, 58, 95, 68, 57, 12, 92, 19, 24, 33, 36, 87, 25, 96, 56, 12, 37, 68, 55, 20, 39, 66, 17, 99, 69, 69, 50, 80, 65, 64, 77, 5, 25, 24, 73, 61, 94, 94, 52, 42, 57, 75, 63, 89, 7, 46, 70, 80, 58, 70, 32, 83, 44, 71, 55, 27, 39, 56, 65, 75, 98, 6, 9, 33, 93, 50, 16, 7, 24, 24, 45, 26, 17, 23, 0, 23, 16, 19, 34, 81, 39, 44, 39, 5, 89, 91, 90, 66, 5, 77, 34, 71, 55, 55, 40, 66, 6, 73, 27, 7], 
	[6, 30, 8, 42, 47, 1, 81, 29, 21, 64, 24, 1, 82, 29, 0, 74, 98, 48, 56, 3, 79, 70, 64, 97, 71, 14, 19, 66, 1, 26, 51, 72, 90, 50, 54, 26, 69, 22, 17, 49, 67, 22, 69, 60, 60, 80, 64, 56, 11, 73, 64, 15, 56, 7, 60, 28, 84, 59, 96, 43, 11, 56, 88, 32, 15, 88, 51, 47, 76, 71, 85, 46, 88, 89, 14, 64, 29, 18, 7, 14, 10, 66, 98, 22, 22, 35, 84, 7, 88, 80, 48, 6, 95, 87, 60, 31, 85, 7, 76, 73], 
	[87, 77, 60, 96, 41, 40, 19, 87, 76, 31, 22, 78, 25, 6, 42, 87, 34, 39, 28, 30, 17, 20, 73, 83, 90, 3, 59, 31, 83, 66, 33, 59, 53, 59, 49, 18, 20, 16, 98, 29, 14, 12, 13, 0, 60, 67, 57, 38, 84, 54, 76, 67, 55, 30, 78, 53, 51, 64, 57, 83, 66, 10, 34, 33, 43, 24, 19, 50, 55, 41, 1, 82, 22, 13, 39, 53, 53, 59, 99, 24, 78, 86, 44, 7, 15, 14, 87, 32, 26, 35, 56, 19, 19, 35, 72, 96, 74, 77, 54, 11], 
	[31, 72, 12, 29, 59, 19, 97, 67, 92, 38, 47, 79, 80, 56, 59, 6, 24, 91, 76, 99, 33, 55, 8, 80, 75, 86, 10, 38, 70, 93, 21, 40, 19, 1, 59, 6, 30, 56, 48, 21, 90, 8, 25, 14, 37, 58, 30, 58, 91, 37, 61, 24, 42, 66, 2, 92, 14, 52, 29, 10, 48, 46, 1, 49, 74, 95, 11, 15, 84, 7, 73, 63, 44, 65, 17, 83, 93, 4, 15, 48, 14, 51, 83, 14, 83, 87, 50, 27, 26, 25, 58, 94, 89, 51, 26, 4, 10, 74, 56, 82], 
	[68, 26, 75, 80, 67, 37, 55, 75, 65, 78, 37, 95, 76, 85, 24, 71, 37, 71, 54, 69, 91, 67, 46, 28, 44, 59, 37, 3, 68, 35, 29, 34, 54, 38, 52, 13, 40, 21, 35, 44, 96, 11, 46, 99, 80, 65, 23, 27, 89, 33, 20, 57, 62, 44, 57, 73, 84, 88, 77, 94, 47, 7, 17, 11, 85, 30, 42, 9, 60, 3, 86, 43, 91, 9, 45, 99, 88, 17, 29, 93, 89, 30, 95, 56, 31, 95, 68, 51, 61, 92, 99, 26, 19, 53, 28, 20, 73, 95, 47, 48], 
	[59, 76, 42, 37, 45, 96, 95, 60, 66, 50, 32, 58, 38, 89, 99, 50, 5, 45, 26, 98, 60, 54, 13, 55, 83, 29, 82, 58, 65, 33, 33, 66, 21, 12, 14, 86, 92, 24, 3, 79, 2, 37, 1, 39, 12, 16, 2, 29, 37, 28, 28, 60, 64, 55, 86, 88, 86, 35, 73, 31, 2, 33, 72, 58, 18, 50, 35, 59, 76, 94, 38, 67, 14, 87, 45, 70, 21, 51, 36, 1, 73, 30, 22, 91, 0, 88, 31, 8, 54, 14, 44, 12, 76, 46, 39, 54, 30, 39, 32, 89], 
	[85, 93, 0, 13, 5, 36, 19, 85, 26, 79, 75, 27, 26, 20, 27, 28, 68, 95, 14, 9, 50, 46, 14, 77, 73, 82, 49, 34, 45, 41, 12, 28, 90, 97, 3, 29, 85, 63, 58, 65, 32, 19, 95, 7, 59, 37, 71, 38, 98, 27, 68, 69, 17, 7, 13, 65, 7, 20, 31, 84, 52, 23, 61, 60, 95, 11, 22, 87, 71, 89, 72, 99, 36, 22, 5, 23, 4, 82, 28, 34, 76, 2, 54, 93, 98, 28, 70, 5, 0, 60, 14, 19, 12, 50, 62, 31, 62, 82, 92, 59], 
	[83, 43, 64, 57, 8, 99, 61, 9, 81, 86, 74, 30, 30, 39, 62, 74, 21, 72, 44, 67, 92, 64, 2, 54, 48, 8, 4, 92, 62, 69, 27, 4, 61, 0, 92, 98, 67, 98, 27, 75, 83, 51, 15, 68, 25, 89, 48, 60, 92, 62, 5, 62, 54, 75, 10, 71, 75, 97, 31, 80, 31, 66, 0, 89, 38, 43, 19, 95, 31, 14, 99, 14, 90, 37, 39, 18, 97, 91, 33, 43, 84, 56, 62, 87, 40, 97, 87, 30, 79, 38, 21, 27, 10, 45, 24, 21, 9, 23, 85, 25]
]
```
This translate to the following talakat script using grammar expansion. The main important part is each array is used to expand a spawner and the boss only spawn the first spawner `spawner_0`.

```python
{
	'spawners': {
		'spawner_9': {
			'pattern': ['bullet'], 
			'patternTime': '4', 
			'patternRepeat': '0', 
			'spawnerPhase': '100', 
			'spawnerRadius': '0', 
			'spawnedNumber': '1, 4, 0.1, 3, circle', 
			'spawnedAngle': 'player', 
			'spawnedSpeed': '4', 
			'bulletRadius': '16'
		}, 
		'spawner_8': {
			'pattern': ['bullet'], 
			'patternTime': '3', 
			'patternRepeat': '0'
		}, 
		'spawner_7': {
			'pattern': ['wait', 'bullet'], 
			'patternTime': '6', 
			'patternRepeat': '0', 
			'spawnerPhase': '70, 240, 2, 4, reverse', 
			'spawnerRadius': '0, 40, 2, 4, reverse'
		}, 
		'spawner_6': {
			'pattern': ['bullet'], 
			'patternTime': '3', 
			'patternRepeat': '5'
		}, 
		'spawner_5': {
			'pattern': ['spawner_7'], 
			'patternTime': '2', 
			'patternRepeat': '3'
		}, 
		'spawner_4': {
			'pattern': ['spawner_5'], 
			'patternTime': '6', 
			'patternRepeat': '0', 
			'spawnerPhase': '110', 
			'spawnerRadius': '40'
		}, 
		'spawner_3': {
			'pattern': ['bullet', 'bullet'], 
			'patternTime': '2', 
			'patternRepeat': '0', 
			'spawnerPhase': '40, 310, -1, 3, reverse', 
			'spawnerRadius': '60', 
			'spawnedNumber': '2, 5, -0.3, 6, reverse', 'spawnedAngle': '350', 
			'spawnedSpeed': '1', 'bulletRadius': '16'
		}, 
		'spawner_2': {
			'pattern': ['bullet'], 
			'patternTime': '3', 
			'patternRepeat': '0', 
			'spawnerPhase': '320', 
			'spawnerRadius': '100', 
			'spawnedNumber': '6', 
			'spawnedAngle': '260', 
			'spawnedSpeed': '2', 
			'bulletRadius': '18, 28, 4, 2, reverse'
		}, 
		'spawner_1': {
			'pattern': ['spawner_6'], 
			'patternTime': '3', 
			'patternRepeat': '1', 
			'spawnerPhase': '30, 270, 2, 2, reverse', 
			'spawnerRadius': '100'
		}, 
		'spawner_0': {
			'pattern': ['bullet'], 
			'patternTime': '6', 
			'patternRepeat': '0', 
			'spawnerPhase': '20', 
			'spawnerRadius': '60', 
			'spawnedNumber': '4', 
			'spawnedAngle': '310', 
			'spawnedSpeed': '3', 
			'bulletRadius': '16'
		}
	}, 
	'boss': {
		'health': 150, 
		'script': [{'health': '1', 'events': ['spawn, spawner_0']}]
	}
}
```
If you want to understand more about the script please check [Talakt Wiki](https://github.com/amidos2006/Talakat/wiki/Scripting-Language).

## Control Parameter
The control parameter is 1D int array about the distribution of the bullets through sections of 30 frames (1 second section). Here is an example showing a pattern of increasing amount of bullets over time:
```python
{
	'bullets': [10, 20, 40, 70, 100]
}
```

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/talakat/__init__.py) file. To add new variant please try to follow the following name structure `talakat-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `width(int)`: the width of the level
- `height(int)`: the height of the level
- `spawnerComplexity(int)`: the number of spawners
- `maxHealth(int)`: the number of frames of the bullet pattern
- `min_bullets(int)`: the minimum number of bullets that need to be on average on screen all the time (optional=50)
- `coverage(float)`: the entropy of the bullet distribution over all the frames (optional=0.95)
- `empty(float)`: the percentage of empty space on screen when there is bullets (optional=0.4)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.5)

An easier way without editing the framework files is to use the `register` function from the `pcg_benchmark` to add the variant.
```python
from pcg_benchmark.probs.talakat import TalakatProblem
import pcg_benchmark

pcg_benchmark.register('talakat-extreme-v0', TalakatProblem, {"width": 200, "height": 300, "spawnerComplexity": 25, "maxHealth": 300})
```

## Quality Measurement
To pass the quality criteria, you need to pass multiple of criteria
- The pattern should be able to be generated without slowing down
- The pattern should have over all the frames equal distribution of bullets in all the areas
- The pattern should have an average of minimum number of bullets on screen
- The pattern should have a percentage of empty area when there is bullets on the screen so the player can protect themselves and stay away from bullets

## Diversity Measurement
To pass the diversity criteria, the distance between the bullet coverage for the every 30 frames of both patterns is different from each other.

## Controlability Measurement
To pass the controlability criteria, you need to make sure that the distribution of bullets over every 30 frames as close as possible to the controlability provided parameters.

## Render Function
This problem is about generating bullet pattern so the render function return an array of images (`PIL.Image`) instead of a single image. To save this array, you can just save every frame independently but that might be too exhausting and too much images. Another way is to save it as `gif` file.

```python
import pcg_benchmark

env = pcg_benchmark.make('talakat-v0')
content = env.content_space.sample()
imgs = env.render(content)
imgs[0].save(os.path.dirname(__file__) + "/images/talakat.gif", save_all=True, optimize=False, append_images=imgs[1:], duration=100, loop=0)
```

If you want instead to save the script instead of the animated bullet pattern, you can change the renderType using the following lines. After you do that you get an image which contains the talakat script. 

```python
import pcg_benchmark

env = pcg_benchmark.make('talakat-v0')
env._problem._render_type = "script"
content = env.content_space.sample()
img = env.render(content)
img.save("talakat.png")
```

If you want to have it as a string istead and save it as json file, please follow the following code instead where the render_type is set to string.

```python
import pcg_benchmark

env = pcg_benchmark.make('talakat-v0')
env._problem._render_type = "string"
content = env.content_space.sample()
script = env.render(content)
with open("talakat.json", "w") as f:
	f.write(script)
```

```python
import pcg_benchmark
from pcg_benchmark.probs.talakat.engine import generateTalakatScript

env = pcg_benchmark.make('talakat-v0')
content = env.content_space.sample()
script = generateTalakatScript(content)
```

## Content Info
This is all the info that you can get about any content using the `info` function:
- `script_connectivity(float)`: the percentage of used spawners to generate the pattern
- `percentage(float)`: is the bullet pattern is being produced and not crashing because of too many bullets or too many spawners
- `bullet_coverage(float)`: the bullet coverage on the screen where 1 means there is bullets everywhere and 0 means bullets are concentrated at one area or no bullets at all.
- `bullets(float[])`: the average number of bullets in every 30 frames
- `bullet_locations(float[][][])`: 3d float array of the heat map of bullets over every 30 frames