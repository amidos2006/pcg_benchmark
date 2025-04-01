<p align="center">
	<img height="50px" src="../../../images/elimination/example.png"/>
</p>
<h1 align="center">
Elimination Problem
</h1>

This is the generation problem for the game [Elimination](http://akhalifa.com/elimination/), you can read about the original generator in ["Elimination from Design to Analysis"](https://arxiv.org/abs/1905.06379). The problem is to generate a sequence of letter that can create at least one short word (3, 4 in length), one long word (5, 6 in length) and nothing longer. Each variant have more additional constraints to make either an easy, normal, or hard level based on how many short and longer words.

The problem has 3 variants:
- `elimination-v0`: generate a sequence of 8 letters for the game elimination with short words lays in 40% to 60% of common words dictionary and long words lays betwen 60% to 80%.
- `elimination-easy-v0`: generate a sequence of 6 letters for the game elimination with short words lays in 10% to 30% of common words dictionary and long words lays betwen 30% to 50%.
- `elimination-hard-v0`: generate a sequence of 10 letters for the game elimination with short words lays in 70% to 90% of common words dictionary and long words lays betwen 80% to 100%.

## Content Structure
The content is a 1D array of integers where the number is which letter in the alphabet (0 is **A** and 25 is **Z**). For example, this is an example with 8 letters which are "LKISDETS"
```python
[ 11, 10, 8, 18, 3, 4, 19, 18 ]
```

## Control Parameter
The control parameter is one parameter on how much of a word have letters after each other and not more. Here is an example where 4 letters has to come after each other to form a word. For example `APPLXE` where it has `APPL` as a sequence from the word `APPLE` after each other. You can't have anything more than 4.
```python
{
    "sequence": 4
}
```
The value of sequence is between 2 and letters.

## Adding a new Variant
If you want to add new variants for this framework, you can add it to [`__init__.py`](https://github.com/amidos2006/pcg_benchmark/blob/main/pcg_benchmark/probs/elimination/__init__.py) file. To add new variant please try to follow the following name structure `elimination-{variant}-{version}` where `{version}` if first time make sure it is `v0`. The following parameter can be changed to create the variant:
- `letters(int)`: the number of letters for the problem
- `short_percentage(float)`: the percentage of short words (3, 4 letter words) that can be constructed from the sequence of letters
- `long_percentage(float)`: the percentage of short words (5, 6 letter words) that can be constructed from the sequence of letters
- `offset(float)`: the size of the short and long percentage. For example if the offset is 0.1 and short percentage is 0.6 then the range is [0.5, 0.7] (optional=0.1)
- `diversity(float)`: the diversity percentage that if you pass it, the diversity value is equal to 1 (optional=0.6)

An easier way without editing the framework files is to use the `register` function from the `pcg_benchmark` to add the variant.
```python
from pcg_benchmark.probs.elimination import EliminationProblem
import pcg_benchmark

pcg_benchmark.register('elimination-extreme-v0', EliminationProblem, {"letters": 20, "short_percentage": 0.5, "long_percentage": 0.9})
```

## Quality Measurement
To pass the quality criteria, you need to pass multiple of criteria
- the letters can construct at least one short word (3, 4 letter word)
- the letters can construct at least one long word (5, 6 letter word)
- the letters can't construct any longer words (7, 8, 9, 10 letter word)
- the short words should lie in the short percentage range [short_percentage-offset, short_percentage+offset]
- the long words should lie in in the long percentage range [long_percentage-offset, long_percentage+offset]
- all words has to be common words

## Diversity Measurement
To pass the diversity criteria, you need the sequence distance ratio between two content more than the diversity parameter.

## Controlability Measurement
To pass the controlability criteria, you need to make sure that none of the words have a sequence of letters follow each other that is more than the control parameter criteria.

## Content Info
This is all the info that you can get about any content using the `info` function:
- `word_3((str,int,bool)[])`|`word_4((str,int,bool)[])`|....|`word_n((str,int,bool)[])`: a list of tuple that consists of 3 values: the word, the longest sequence of that word exists in the letters provided, and if the word is common or not. The value after `word_` is the number of letters this word is consisting of.