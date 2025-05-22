# standard imports

# local imports
from game import Game
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class WorldInterface(object):
    """
    This class provides an interface to all game information required by the AI.
    """
    @property
    def star_date(self):
        """
        Return the current star date.
        :return: The current star date, as int.
        """
        return glob_vars.the_game.star_date

    @property
    def time_remaining(self):
        """
        Return the time remaining in the game.
        :return: The time remaining in the game, as int.
        """
        return glob_vars.the_game.time_remaining

    @property
    def energy(self):
        """
        Return the current energy level.
        :return: The current energy level, as int.
        """
        return glob_vars.the_game.energy

    @property
    def klingons(self):
        """
        Return the number of Klingons remaining in the game.
        :return: The number of Klingons, as int.
        """
        return glob_vars.the_game.klingons

    @property
    def starbases(self):
        """
        Return the number of starbases remaining in the game.
        :return: The number of starbases, as int.
        """
        return glob_vars.the_game.starbases

    @property
    def quadrant_x(self):
        """
        Return the current quadrant x-coordinate, [0..7].
        :return: The current quadrant x-coordinate, as int.
        """
        return glob_vars.the_game.quadrant_x

    @property
    def quadrant_y(self):
        """
        Return the current quadrant y-coordinate, [0..7].
        :return: The current quadrant y-coordinate, as int.
        """
        return glob_vars.the_game.quadrant_y
    
    @property
    def sector_x(self):
        """
        Return the current sector x-coordinate, [0..7].
        :return: The current sector x-coordinate, as int.
        """
        return glob_vars.the_game.sector_x

    @property
    def sector_y(self):
        """
        Return the current sector y-coordinate, [0..7].
        :return: The current sector y-coordinate, as int.
        """
        return glob_vars.the_game.sector_y

    @property
    def shield_level(self):
        """
        Return the current shield level.
        :return: The current shield level, as int.
        """
        return glob_vars.the_game.shield_level

    @property
    def navigation_damage(self):
        """
        Return the current navigation damage level.
        :return: The current navigation damage level, as int.
        """
        return glob_vars.the_game.navigation_damage

    @property
    def short_range_scan_damage(self):
        """
        Return the current short range scan damage level.
        :return: The current short range scan damage level, as int.
        """
        return glob_vars.the_game.short_range_scan_damage

    @property
    def long_range_scan_damage(self):
        """
        Return the current long range scan damage level.
        :return: The current long range scan damage level, as int.
        """
        return glob_vars.the_game.long_range_scan_damage

    @property
    def shield_control_damage(self):
        """
        Return the current shield control damage level.
        :return: The current shield control damage level, as int.
        """
        return glob_vars.the_game.shield_control_damage

    @property
    def computer_damage(self):
        """
        Return the current computer damage level.
        :return: The current computer damage level, as int.
        """
        return glob_vars.the_game.computer_damage

    @property
    def photon_torpedo_damage(self):
        """
        Return the current photon torpedo damage level.
        :return: The current photon torpedo damage level, as int.
        """
        return glob_vars.the_game.photon_damage
    
    @property
    def phaser_damage(self):
        """
        Return the current phaser control damage level.
        :return: The current phaser control damage level, as int.
        """
        return glob_vars.the_game.phaser_damage

    @property
    def photon_torpedoes(self):
        """
        Return the current number of remaining photon torpedoes.
        :return: The current number of remaining photon torpedoes, as int.
        """
        return glob_vars.the_game.photon_torpedoes

    @property
    def docked(self):
        """
        Return whether the Enterprise is currently docked at a starbase.
        :return: True if the Enterprise ship is docked, False otherwise, as boolean.
        """
        return glob_vars.the_game.docked

    @property
    def destroyed(self):
        """
        Return whether the Enterprise has been destroyed.
        :return: True if the Enterprise has been destroyed, False otherwise, as boolean.
        """
        return glob_vars.the_game.destroyed

    @property
    def starbase_x(self):
        """
        Return the x-coordinate sector of the starbase, if and only if there is a starbase in the current quadrant.
        :return: The x-coordinate sector of the starbase in the current quadrant, as int.
        :raise: AssertionError if there is no starbase in the current quadrant.
        """
        assert(glob_vars.the_game.quadrants[glob_vars.the_game.quadrant_y][glob_vars.the_game.quadrant_x].starbase)
        return glob_vars.the_game.starbase_x

    @property
    def starbase_y(self):
        """
        Return the y-coordinate sector of the starbase, if and only if there is a starbase in the current quadrant.
        :return: The y-coordinate sector of the starbase in the current quadrant, as int.
        :raise: AssertionError if there is no starbase in the current quadrant.
        """
        assert(glob_vars.the_game.quadrants[glob_vars.the_game.quadrant_y][glob_vars.the_game.quadrant_x].starbase)
        return glob_vars.the_game.starbase_y

    @property
    def quadrants(self):
        """
        Return the list of quadrant's in the game..
        :return: A (new) list of the game's quadrants, as [Quadrant objects].
        """
        return list(glob_vars.the_game.quadrants)

    @property
    def quadrant(self):
        """
        Return the current quadrant in the game, that is, the quadrant the Enterprise is currently in.
        :return: The quadrant the Enterprise is currently in, as Quadrant object.
        """
        return glob_vars.the_game.quadrants[glob_vars.the_game.quadrant_y][glob_vars.the_game.quadrant_x]
    
    @property
    def sectors(self):
        """
        Return the list of sectors in the current quadrant, with each sector represented as an int defined
        by the class SectorType().
        :return: A (new) list of the sectors in the current quadrant, as [int].
        """
        return list(glob_vars.the_game.sector)

    @property
    def klingon_ships(self):
        """
        Return the list of Klingon ships in the current quadrant.
        :return: A (new) list of the Klingon ships in the current quadrant, as [KlingonShip objects].
        """
        return list(glob_vars.the_game.klingon_ships)
    



