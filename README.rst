================
 Star Trek 1971
================
------------
 for Python
------------

About
=====

I recently discovered the classic old BASIC game `Star Trek`_ from 1971, through a post seen on Reddit_.

The post contained a version of the game rewritten in C-Sharp which I thought was quite good.
I wondered if anyone had ported it to Python.

After a little bit of research, I didn't find a definitive version for Python.

This is by no means a definitive version itself; I just took the C# version and converted it to Python.

.. _Star Trek: http://en.wikipedia.org/wiki/Star_Trek_%28text_game%29
.. _Reddit: http://www.codeproject.com/Articles/28228/Star-Trek-Text-Game

Change Log
==========

April 2025 (Kevin R. Geurts, kevin.r.geurts@gmail.com)

(1)	Updated startrek.py for Python 3.x: Print is a now a function and not a statement and requres ().
(2) Updated startrek.py for Python 3.x: raw_input() is now input().
(3) In startrek.py, fixed bug in input_double(). Attempting to turn a bad input string into a float results in a ValueError exception.
(4) In startrek.py, removed duplication of shield control command prompt in shield_controls().
(5) In startrek.py, Game.sector list of lists items now initialized with int() not SectorType().
	This was harmless, since items got overwritten with ints anyway before being accessed, but confusing.
(6) In startrek.py, in navigation(): (a) fixed bugs in integer and mod division.
	(b) fixed off-by-one index error in is_docking_location(). These bugs caused docking with starbase to fail.
(7) In startrek.py, added some dock strings to clarify a few functions' parameters.
(8) In startrek.py, fixed bug that Game.starbase_x and Game.starbase_y were not set to 0 in initialize_game().
(9) In startrek.py, added support for /d flag to __main__ to trigger a DEBUG mode which consistently seeds the random number generator.
	This is helpful in testing.
(10) In test_startrek.py, created a total of 78 passing unittests. All functions are tested, although a small number of
	TODO comments denote potential coverage improvements.
(11) In startrek.py, added hint to request for navigation course to indicated up, down, left, right meaning of course number.
(12) In startrek.py, added hint to request for photon torpedo firing direction to indicate up, down, left, right meaning of numeric direction.
(13) In startrek.py, fixed bug in initialize_game() that caused there to be a far more starbases present in the galaxy than intended.
	 Updated unittest in test_startrek.py to assert that this is not happening.

Improvements
============

There's heaps that can be done with this program. A lot of implementations used global variables.
I tried to fix this by encapsulating them in a global object, but this can definitely be improved further.

Here is a list of possible improvements:

- Encapsulate everything in classes
- Include help/instructions
- Add extra features;
   + new ships, celestial objects, etc
   + new weapon types
   + crew functions
- Easier navigation (using cartesian system maybe)
- Make some parts more 'Pythonic'
- ...Plenty more!