# pyStarTrek

Source code: [GitHub](https://github.com/KevinRGeurts/pyStarTrek)
---
pyStarTrek is a Python implementation of the classic text-based game Star Trek from 1971.

This project began as a fork of [cosmicr/startrek1971](https://github.com/cosmicr/startrek1971). The change log
section below details the modifications made subsequent to the fork. In summary:

1. Code was updated to Python 3.x.
2. Unit tests were added and identified bugs were fixed.
3. Significant code refactoring was performed to improve readability and maintainability, and to begin encapsulation.
4. A Goal Oriented Behavior AI player option was added to allow automated gameplay. Think of this as a very simple platform for experimenting with game AI.

## Requirements

- pyGameAIFoundation>=0.1.1: [GitHub](https://github.com/KevinRGeurts/pyGameAIFoundation), [PyPi](https://pypi.org/project/pyGameAIFoundation/)

## Change Log

April-December, 2025 (Kevin R. Geurts, kevin.r.geurts@gmail.com)

1. Updated startrek.py for Python 3.x: Print is a now a function and not a statement and requres ().
2. Updated startrek.py for Python 3.x: raw_input() is now input().
3. In startrek.py, fixed bug in input_double(). Attempting to turn a bad input string into a float results in a ValueError exception.
4. In startrek.py, removed duplication of shield control command prompt in shield_controls().
5. In startrek.py, Game.sector list of lists items now initialized with int() not SectorType().
	This was harmless, since items got overwritten with ints anyway before being accessed, but confusing.
6. In startrek.py, in navigation(): (a) fixed bugs in integer and mod division.
	(b) fixed off-by-one index error in is_docking_location(). These bugs caused docking with starbase to fail.
7. In startrek.py, added some dock strings to clarify a few functions' parameters.
8. In startrek.py, fixed bug that Game.starbase_x and Game.starbase_y were not set to 0 in initialize_game().
9. In startrek.py, added support for /d flag to __main__ to trigger a DEBUG mode which consistently seeds the random number generator.
	This is helpful in testing.
10. In test_startrek.py, created a total of 78 passing unittests. All functions are tested, although a small number of
	TODO comments denote potential coverage improvements.
11. In startrek.py, added hint to request for navigation course to indicated up, down, left, right meaning of course number.
12. In startrek.py, added hint to request for photon torpedo firing direction to indicate up, down, left, right meaning of numeric direction.
13. In startrek.py, fixed bug in initialize_game() that caused there to be a far more starbases present in the galaxy than intended.
	 Updated unittest in test_startrek.py to assert that this is not happening.
14. In startrek.py, added sector coordinate numbers to short range scan print.

## Improvements

In addition to potential improvements listed for the original project, here are some more ideas: 

1. Add additional "cheat codes" as command line arguments: infinite energy, infinite torpedos, stronger phasers.
2. Add quadrant coordinate numbers on long range scan and galactic record output.
3. cloaked klingon ships that don't appear on long range scan or galactic record until they have been short range scanned, because then they would have dropped cloak to potentially attack Enterprise.
4. Wormhole with entry/exit in two different quadrants, that provides instant, no energy passage from one quadrant to the other when Enterprise "docks" or "collides" with it. Could have a random risk of damaging Enterprise.
5. Display torpedo track as "." on short range scan, instead of as a list of sector coordinates.

## Basic usage

The simplest way to run the game is:

```
python .\startrek.py
```

## Unittests

Unittests for pyStarTrek have filenames starting with test_. To run the unittests,
type ```python -m unittest discover -s . -v``` in a terminal window in the project directory.

## License
MIT License. See the LICENSE file for details
