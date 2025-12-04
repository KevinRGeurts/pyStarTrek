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


Usage
=====

To play the game, type 'python startrek.py' in a terminal window.
To run the unit tests, type 'python -m unittest discover' in a terminal window.


Change Log
==========

April-December, 2025 (Kevin R. Geurts, kevin.r.geurts@gmail.com)

In the list below, items marked {ai} are additions or refactors made to facilitate future addition of AI-driven, automatic game play.
Items marked {gui} are additions or refactors made to facilitate future additon of a GUI.

(1)	Updated startrek.py for Python 3.x: Print is a now a function and not a statement and requres ().
(2) Updated startrek.py for Python 3.x: raw_input() is now input().
(3) In startrek.py, fixed bug in input_double(). Attempting to turn a bad input string into a float results in a ValueError exception.
(4) In startrek.py, removed duplication of shield control command prompt in shield_controls().
(5) In startrek.py, Game.sector list of lists items now initialized with int() not SectorType().
	This was harmless, since items got overwritten with ints anyway before being accessed, but confusing.
(6) In startrek.py, in navigation(): (a) fixed bugs in integer and mod division.
	(b) fixed off-by-one index error in is_docking_location(). These bugs caused docking with starbase to fail.
(7) In startrek.py, added some doc strings to clarify a few functions' parameters.
(8) In startrek.py, fixed bug that Game.starbase_x and Game.starbase_y were not set to 0 in initialize_game().
(9) In startrek.py, added support for /d flag to __main__ to trigger a DEBUG mode which consistently seeds the random number generator.
	This is helpful in testing.
(10) Moved the "game" variable in startrek.py to "the_game" in glob_vars.py.
(11) Moved Quadrant and Game classes out of glob_vars.py and into quadrant.py and game.py.
(12) Moved four functions that don't access the game state out of startrek.py and into utilities.py. For example, distance(). Added doc strings to utilities.py.
(13) In test_startrek.py, test_quadrant.py, and test_utilities.py created a total of 105 passing unittests.
(14) In startrek.py, added hint to request for navigation course to indicated up, down, left, right meaning of course number.
(15) In startrek.py, added hint to request for photon torpedo firing direction to indicate up, down, left, right meaning of numeric direction.
(16) In startrek.py, fixed bug in initialize_game() that caused there to be a far more starbases present in the galaxy than intended.
	 Updated unittest in test_startrek.py to assert that this is not happening.
(17) In startrek.py, added sector coordinate numbers to short range scan print.
(18) In startrek.py, fixed bug that allowed shield energy to be adjusted when shield control was damaged.
(19) {gui}{ai} In startrek.py, short range scan, long range scan, phaser control, torpedo control, shield control, and navigation all modified to
	 separate prechecks, input, and execution, and to capture output into list of strings, in preparation for either
	 capturing output for GUI or driving game play through AI.
(20) {ai} In startrek.py, refactored display_galactic_record() to use _fetch_galactic_record().
(21) {gui}{ai} In startrek.py, refactored induce_damage(...) to return a list of strings to be printed.
(22) {ai} In startrek.py, startrek._navigation(...) now returns a boolean indicating if an obstacle was encountered.
(23) {ai} In utilities.py, created StarTrekCourse class to represent direction in Star Trek navigation, and allowing addition/subtraction to adjust direction. 
(24) {ai} In startrek.py, _phaser_controls_fire(...) now returns number of klingon ships destroyed, and _torpedo_control_launch(...) now returns booleans indicateding
     if torpedo missed everything and if torpedo was captured by star.
(25) In startrek.py and game.py added python logging, and /log command line option to log navigation data for debugging purposes.
(26) Added GameOptions class to retain game options set by command line arguments.
(27) Added GameOptions.cheat_no_damage, set to True by /no_damage command line argument.


Improvements
============

There's heaps that can be done with this program. A lot of implementations used global variables.
I tried to fix this by encapsulating them in a global object, but this can definitely be improved further.

Here is a list of possible improvements:

- Encapsulate everything in classes
- Include help/instructions
- Add "cheat codes" as command line arguments: infinite energy, infinite torpedos, stronger phasers
- Add extra features;
   + new ships, celestial objects, etc
   + new weapon types
   + crew functions
   + quadrant coordinate numbers shown on long range scan and galactic record
   + cloaked klingon ships that don't appear on long range scan or galactic record until they have been short range
		scanned, because they they would have dropped cloak to potentially attack Enterprise
   + wormhole with entry/exit in two different quadrants, that provides instant, no energy passage from one
		quadrant to the other when Enterprise "docks" or "collides" with it. Could have a random risk of damaging
		Enterprise.
   + display torpedo track as "." on short range scan, instead of as a list of sector coordinates
- Easier navigation (using cartesian system maybe)
- Make some parts more 'Pythonic'
- ...Plenty more!