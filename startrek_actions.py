# standard imports

# local imports
from game_action import GameAction
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.

# TODO: Create unit tests

class NavigateToQuadrantAction(GameAction):
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

    def execute(self):
        """
        Execute the navigation action.
        :return: None
        """
        gm=glob_vars.the_game
        # Make sure we aren't trying to navigate to the same quadrant
        assert(gm.quadrant_x != self.qx or gm.quadrant_y != self.qy)
        # Placeholder for actual navigation logic
        print(f"Navigating to quadrant ({self.qx+1}, {self.qy+1})")
        # Determine distance to target quadrant
        dist = startrek.distance(gm.quadrant_x, gm.quadrant_y, self.qx, self.qy)
        # Determine direction to target quadrant
        direction = startrek.compute_direction(gm.quadrant_x, gm.quadrant_y, self.qx, self.qy)
        # Perform navigation
        # TODO: Handle hitting an obstacle leaving current quadrant
        output = startrek._navigation(direction, dist)
        # TODO: Check if navigation was successful
        self._completed = True
        startrek.print_strings(output)
        

