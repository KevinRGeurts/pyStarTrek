# standard imports
from enum import StrEnum

# local imports
from math import exp
from game_action import GameAction
from game_goal import GameGoal, GoalInsistence
from startrek_goals import SurviveGoal, FindKlingonShipGoal
from world_interface import WorldInterface
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class BlackboardDatumType(StrEnum):
    """
    Enumeration of the types of data that can be written to the blackboard in a Star Trek game.
    """
    KLINGON_QUAD_X = 'klingon_quad_x'
    KLINGON_QUAD_Y = 'klingon_quad_y'
    BASE_QUAD_X = 'base_quad_x'
    BASE_QUAD_Y = 'base_quad_y'


class StarTrekAction(GameAction):
    """
    Base class for all Star Trek game actions. Provides access to WorldInterface.
    """
    def __init__(self, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        self._world = WorldInterface()


class LongRangeScanAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player performs a long-range scan of the surrounding
    quadrants, with intent to find a Klingon Ship or a Starbase.
    """
    def __init__(self, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        self._is_complete = False
    
    def execute(self):
        """
        Execute the long range scan action.
        :return: None
        """
        # Check if long range scanner is damaged.
        (possible, output) = startrek.long_range_scan_precheck()
        if not possible:
            # Long range scanner is damaged, and cannot be used
            startrek.print_strings(output)
            return
        # Perform the long range scan
        scan_output = startrek._long_range_scan()
        # Find the first quadrant, if any, in the scan, that has a klingon ship.
        quad_x = self._world.quadrant_x
        quad_y = self._world.quadrant_y
        klingon_quad_x = -1
        klingon_quad_y = -1
        try:
            for i in range(3):
                for j in range(3):
                    if int(scan_output[i][j][0]) > 0:
                        klingon_quad_x = quad_x + j - 1
                        klingon_quad_y = quad_y + i - 1
                        raise StopIteration  # Break out of both loops when the first klingon ship is found
        except StopIteration:
            pass
        # If a klingon ship was found, write coordinates to blackboard, if we have one
        if klingon_quad_x >= 0 and klingon_quad_y >= 0:
            if self._write_blackboard is not None:
                self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_X, klingon_quad_x)
                self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_Y, klingon_quad_y)
        
        # Find the first quadrant, if any, in the scan, that has a starbase.
        base_quad_x = -1
        base_quad_y = -1
        try:
            for i in range(3):
                for j in range(3):
                    if int(scan_output[i][j][1]) > 0:
                        base_quad_x = quad_x + j - 1
                        base_quad_y = quad_y + i - 1
                        raise StopIteration  # Break out of both loops when the first klingon ship is found
        except StopIteration:
            pass
        # If a klingon ship was found, write coordinates to blackboard, if we have one
        if base_quad_x >= 0 and base_quad_y >= 0:
            if self._write_blackboard is not None:
                self._write_blackboard(BlackboardDatumType.BASE_QUAD_X, base_quad_x)
                self._write_blackboard(BlackboardDatumType.BASE_QUAD_Y, base_quad_y)
        self._is_complete = True  # Mark the action as complete after the scan is executed, regardless of results.
        return

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        return self._is_complete

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with completing the long range scan.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with completing the long range scan, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, FindKlingonShipGoal):
            # Not to be taken literally, but simply to indicated that completing this action will lower
            # the insistence of the FindKlingonShipGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO


class RaiseShieldsAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player raises the shields.
    """
    def __init__(self, shield_energy=0, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        Initialize the RaiseShieldsAction object.
        :param shield_energy: The desired energy level for the shields, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        assert(shield_energy >= 0)
        self._shield_energy = shield_energy

    def execute(self):
        """
        Execute the raise shields action.
        :return: None
        """
        # Check if shield controls are damaged.
        (possible, output) = startrek._shield_controls_precheck()
        if not possible:
            # Shield control is damaged, and shields cannot be adjusted
            startrek.print_strings(output)
            return
        # Check what level shields are currently at
        current_shields = self._world.shield_level
        # Check if shields are already at the desired level
        if current_shields == self._shield_energy:
            # Shields are already at the desired level
            startrek.print_strings(["Shields are already at the desired level."])
            return
        # Are we trying to increase shield enregy?
        elif self._shield_energy > current_shields:
            # Check if we have enough energy to raise shields
            if (self._shield_energy - current_shields) > self._world.energy:
                # Not enough energy to raise shields
                startrek.print_strings([f"Not enough energy to increase shields to {self._shield_energy}."])
                return
            else:
                # Add to shield energy
                output = startrek._shield_controls_adjust(True, self._shield_energy)
                startrek.print_strings(output)
        # Are we trying to decrease shield energy?
        else:
            # If we are asking to lower the shields to zero, then we'll just lower them to zero
            output=[] # list of strings to print
            if (self._shield_energy) == 0:
                output = startrek._shield_controls_adjust(False, current_shields)
            else:
                # Lower the shields (subtract energy) by an amount needed to get them at the desired level
                output = startrek._shield_controls_adjust(False, (current_shields - self._shield_energy))
            startrek.print_strings(output)
        return

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        # Check if the current shield energy matches the desired shield energy. If it does, then the action was
        # successful, and the action is complete.
        if self._world.shield_level == self._shield_energy:
            # Raising shields was successful
            return True
        else:
            return False

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with raising the shields.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with raising the shields, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, SurviveGoal):
            # Not to be taken literally, but simply to indicated that completing this action will lower
            # the insistence of the SurviveGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO
        

class NavigateToQuadrantAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player navigates to a specific quadrant.
    """
    def __init__(self, qx=1, qy=1, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :param qx: The quadrant x-coordinate [0..7] to navigate to, as int.
        :param qy: The quadrant y-coordinate [0..7] to navigate to, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
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

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with navigating to the target quadrant.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with navigating to the target quadrant, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, FindKlingonShipGoal):
            # Not to be taken literally, but simply to indicated that completing this action
            # to get to a target quandrant with a Klingon ship will lower the insistence of the FindKlingonShipGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO
        

