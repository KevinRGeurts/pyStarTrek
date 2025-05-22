# standard imports

# local imports
from game_action import GameAction
from world_interface import WorldInterface
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.

class StarTrekAction(GameAction):
    """
    Base class for all Star Trek game actions. Provides access to WorldInterface.
    """
    def __init__(self, expiry_time=0, priority=0):
        """
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        """
        super().__init__(expiry_time, priority)
        self._world = WorldInterface()


class NavigateToQuadrantAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player navigates to a specific quadrant.
    """
    def __init__(self, qx=1, qy=1, expiry_time=0, priority=0):
        """
        :param qx: The quadrant x-coordinate [0..7] to navigate to, as int.
        :param qy: The quadrant y-coordinate [0..7] to navigate to, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        """
        super().__init__(expiry_time, priority)
        assert(qx>=0 and qx<=7)
        self.qx = qx
        assert(qy>=0 and qy<=7)
        self.qy = qy

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        # Check if the current game quadrant matches the target quadrant. If it does, then navigation was
        # successful, and the action is complete.
        if self._world.quadrant_x == self.qx and self._world.quadrant_y == self.qy:
            # Navigation was successful
            return True
        else:
            return False

    def execute(self):
        """
        Execute the navigation action.
        :return: None
        """
        # Make sure we aren't trying to navigate to the same quadrant
        assert(self._world.quadrant_x != self.qx or self._world.quadrant_y != self.qy)
        # Placeholder for actual navigation logic
        print(f"Navigating to quadrant ({self.qx+1}, {self.qy+1})")
        # Determine distance to target quadrant
        dist = startrek.distance(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
        # Determine direction to target quadrant
        direction = startrek.compute_direction(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
        # Perform navigation
        # TODO: Handle hitting an obstacle leaving current quadrant
        output = startrek._navigation(direction, dist)
        startrek.print_strings(output)
        

