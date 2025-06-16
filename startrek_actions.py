# standard imports
from enum import StrEnum

# local imports
from math import exp
from game_action import GameAction, GameActionSequence
from game_goal import GameGoal, GoalInsistence
from startrek_goals import DestroyKlingonShipGoal, ExploreGalaxyGoal, SurviveGoal, FindKlingonShipGoal
from utilities import StarTrekCourse
from world_interface import WorldInterface
from exceptions import ActionCannotAchieveGoalError
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
    UNSCANNED_QUAD_X = 'unscanned_quad_x'
    UNSCANNED_QUAD_Y = 'unscanned_quad_y'    

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


class ExploreUnknownRegionAction(GameActionSequence):
    """
    Represents a sequence of actions in a Star Trek game where a player checks the galactic record
    to find a quadrant that has not been scanned, then navigates to that quadrant, then performs a long-range scan.
    :param expiry_time: The time in an arbitrary count-up from zero until the action sequence expires, as int.
    :param priority: The priority of the action sequence. Higher numbers indicate higher priority. As int.
    """
    def __init__(self, expiry_time=0, priority=0):
        rec_act = FindUnscannedQuadrantAction(read_blackboard=self.readFromBlackBoard,
                                              write_blackboard=self.writeToBlackBoard)
        nav_act = NavigateToQuadrantAction(looking_for='unscanned',
                                           read_blackboard=self.readFromBlackBoard,
                                           write_blackboard=self.writeToBlackBoard)
        super().__init__(expiry_time, priority, seq_acts=[rec_act, nav_act])


class FindKlingonShipAction(GameActionSequence):
    """
    Represents a sequence of actions in a Star Trek game where a player scans and checks the galactic record
    to find a quadrant with a Klingon ship, and then navigates to that quadrant.
    :param expiry_time: The time in an arbitrary count-up from zero until the action sequence expires, as int.
    :param priority: The priority of the action sequence. Higher numbers indicate higher priority. As int.
    """
    def __init__(self, expiry_time=0, priority=0):
        scan_act = LongRangeScanAction(read_blackboard=self.readFromBlackBoard,
                                       write_blackboard=self.writeToBlackBoard)
        rec_act = CheckGalacticRecordAction(read_blackboard=self.readFromBlackBoard,
                                            write_blackboard=self.writeToBlackBoard)
        nav_act = NavigateToQuadrantAction(read_blackboard=self.readFromBlackBoard,
                                           write_blackboard=self.writeToBlackBoard)
        super().__init__(expiry_time, priority, seq_acts=[scan_act, rec_act, nav_act])


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

        # Look for a quadrant with a klingon ship in the long range scan, unless coordinates of a quadrant
        # with a klingon ship were already written to the blackboard.
        if self._read_blackboard is not None and \
           self._read_blackboard(BlackboardDatumType.KLINGON_QUAD_X) is None:

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
                    print(f"LongRangeScanAction found Klingon ship at quadrant ({klingon_quad_x+1}, {klingon_quad_y+1}).")
                    self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_X, klingon_quad_x)
                    self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_Y, klingon_quad_y)

        # Look for a quadrant with a starbase in the long range scan, unless coordinates of a quadrant
        # with a starbase were already written to the blackboard.
        if self._read_blackboard is not None and \
           self._read_blackboard(BlackboardDatumType.BASE_QUAD_X) is None:
        
            # Find the first quadrant, if any, in the scan, that has a starbase.
            base_quad_x = -1
            base_quad_y = -1
            try:
                for i in range(3):
                    for j in range(3):
                        if int(scan_output[i][j][1]) > 0:
                            base_quad_x = quad_x + j - 1
                            base_quad_y = quad_y + i - 1
                            raise StopIteration  # Break out of both loops when the first starbase is found
            except StopIteration:
                pass
            # If a starbase was found, write coordinates to blackboard, if we have one
            if base_quad_x >= 0 and base_quad_y >= 0:
                print(f"LongRangeScanAction found starbase at quadrant ({base_quad_x+1}, {base_quad_y+1}).")
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


class FindUnscannedQuadrantAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player finds an unscanned quadrant in the galactic record.
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
        Execute the find unscanned quadrant action.
        :return: None
        """
        # TODO: An improvement here would be to find the unscanned quadrant that is closest to
        # the Enterprise's current quadrant, rather than just taking the first one found in the galactic record.
        # And further, finding one that would maximize the number of new quadrants scanned.
        # As is, this action will waste energy (to navigate) and time.

        # Check if computer control is damaged.
        (possible, output) = startrek._computer_controls_precheck()
        if not possible:
            # Computer control is damaged, and cannot be used
            startrek.print_strings(output)
            return
        # Obtain the galactic record
        rec_output = startrek._fetch_galactic_record()

        # Look for an unscanned quadrant in the galactic record, unless coordinates of an unscanned quadrant
        # were already written to the blackboard.
        if self._read_blackboard is not None and \
           self._read_blackboard(BlackboardDatumType.UNSCANNED_QUAD_X) is None:

            # Find the first quadrant, if any, in the record, that has 0 stars, indicating it hasn't been scanned yet.
            unscanned_quad_x = -1
            unscanned_quad_y = -1
            try:
                for i in range(8):
                    for j in range(8):
                        if int(rec_output[i][j][2]) == 0:
                            unscanned_quad_x = j
                            unscanned_quad_y = i
                            raise StopIteration  # Break out of both loops when the first unscanned quadrrant is found
            except StopIteration:
                pass
            # If an unscanned quadrant was found, write coordinates to blackboard, if we have one.
            if unscanned_quad_x >= 0 and unscanned_quad_y >= 0:
                if self._write_blackboard is not None:
                    print(f"FindUnscannedQuadrantAction found unscanned quadrant ({unscanned_quad_x+1}, {unscanned_quad_y+1}).")
                    self._write_blackboard(BlackboardDatumType.UNSCANNED_QUAD_X, unscanned_quad_x)
                    self._write_blackboard(BlackboardDatumType.UNSCANNED_QUAD_Y, unscanned_quad_y)
        
        self._is_complete = True  # Mark the action as complete after the galactic record is checked, regardless of results.
        return

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        return self._is_complete

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with completing the check of the galactic record.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with completing the check of the galactic record, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, ExploreGalaxyGoal):
            # Not to be taken literally, but simply to indicated that completing this action will lower
            # the insistence of the FindKlingonShipGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO


class CheckGalacticRecordAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player checks the computer's galactic record,
    with intent to find a Klingon Ship or a Starbase.
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
        Execute the check galactic record action.
        :return: None
        """
        # TODO: An improvement here would be to find the klingon ship or starbase that is closest to
        # the Enterprise's current quadrant, rather than just taking the first one found in the galactic record.
        # As is, this action will waste energy (to navigate) and time.

        # Check if computer control is damaged.
        (possible, output) = startrek._computer_controls_precheck()
        if not possible:
            # Computer control is damaged, and cannot be used
            startrek.print_strings(output)
            return
        # Obtain the galactic record
        rec_output = startrek._fetch_galactic_record()

        # Look for a quadrant with a klingon ship in the galactic record, unless coordinates of a quadrant
        # with a klingon ship were already written to the blackboard.
        if self._read_blackboard is not None and \
           self._read_blackboard(BlackboardDatumType.KLINGON_QUAD_X) is None:

            # Find the first quadrant, if any, in the record, that has a klingon ship.
            klingon_quad_x = -1
            klingon_quad_y = -1
            try:
                for i in range(8):
                    for j in range(8):
                        if int(rec_output[i][j][0]) > 0:
                            klingon_quad_x = j
                            klingon_quad_y = i
                            raise StopIteration  # Break out of both loops when the first klingon ship is found
            except StopIteration:
                pass
            # If a klingon ship was found, write coordinates to blackboard, if we have one.
            if klingon_quad_x >= 0 and klingon_quad_y >= 0:
                if self._write_blackboard is not None:
                    print(f"CheckGalacticRecordAction found Klingon ship at quadrant ({klingon_quad_x+1}, {klingon_quad_y+1}).")
                    self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_X, klingon_quad_x)
                    self._write_blackboard(BlackboardDatumType.KLINGON_QUAD_Y, klingon_quad_y)

        # Look for a quadrant with a starbase in the galactic record, unless coordinates of a quadrant
        # with a starbase were already written to the blackboard.
        if self._read_blackboard is not None and \
           self._read_blackboard(BlackboardDatumType.BASE_QUAD_X) is None:
        
            # Find the first quadrant, if any, in the scan, that has a starbase.
            base_quad_x = -1
            base_quad_y = -1
            try:
                for i in range(8):
                    for j in range(8):
                        if int(rec_output[i][j][1]) > 0:
                            base_quad_x = j
                            base_quad_y = i
                            raise StopIteration  # Break out of both loops when the first starbase is found
            except StopIteration:
                pass
            # If a starbase was found, write coordinates to blackboard, if we have one
            if base_quad_x >= 0 and base_quad_y >= 0:
                print(f"CheckGalacticRecordAction found starbase at quadrant ({base_quad_x+1}, {base_quad_y+1}).")
                if self._write_blackboard is not None:
                    self._write_blackboard(BlackboardDatumType.BASE_QUAD_X, base_quad_x)
                    self._write_blackboard(BlackboardDatumType.BASE_QUAD_Y, base_quad_y)
        
        self._is_complete = True  # Mark the action as complete after the galactic record is checked, regardless of results.
        return

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        return self._is_complete

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with completing the check of the galactic record.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with completing the check of the galactic record, as int.
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
        print(f"RaiseShieldsAction attempting to set shield energy to {self._shield_energy}.")
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
                output = startrek._shield_controls_adjust(True, self._shield_energy - current_shields)
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
 
        
# TODO: Having the looking_for parameter to __init__ is a bit of a hack, and definitely not OO. It would be better to have separate actions, perhaps.
class NavigateToQuadrantAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player navigates to a specific quadrant.
    """
    def __init__(self, looking_for='klingon', qx=None, qy=None, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :parameter looking_for: The type of quadrant to navigate to, as str.
            Valid strings are: 'klingon', 'starbase', 'unscanned'.    
            Determines which location data to look for on the blackboard.
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
        self._looking_for = looking_for
        if qx is not None: assert(qx>=0 and qx<=7)
        self.qx = qx
        if qy is not None: assert(qy>=0 and qy<=7)
        self.qy = qy
        # How many times have we attempted to navigate to the target quadrant?
        self._attempts = 0
        self._max_attempts = 2  # If we attempt to navigate to the same quadrant too many times, we'll give up.

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
        elif self._attempts > self._max_attempts:
            # If we have attempted to navigate to the target quadrant too many times, then we give up.
            startrek.print_strings(["NavigateToQuadrantAction failed: too many attempts to navigate to the same quadrant."])
            return True
        else:
            return False

    def execute(self):
        """
        Execute the navigation action.
        :return: None
        """

        self._attempts += 1

        # If we don't have target quadrant coordinates, then we need to read them from the blackboard.
        if self.qx is None:
            assert(self._read_blackboard is not None)
            match self._looking_for:
                case 'klingon':
                    self.qx = self._read_blackboard(BlackboardDatumType.KLINGON_QUAD_X)
                case 'starbase':
                    self.qx = self._read_blackboard(BlackboardDatumType.BASE_QUAD_X)    
                case 'unscanned':
                    self.qx = self._read_blackboard(BlackboardDatumType.UNSCANNED_QUAD_X)    
        if self.qy is None:
            assert(self._read_blackboard is not None)
            match self._looking_for:
                case 'klingon':
                    self.qy = self._read_blackboard(BlackboardDatumType.KLINGON_QUAD_Y)
                case 'starbase':
                    self.qy = self._read_blackboard(BlackboardDatumType.BASE_QUAD_Y)    
                case 'unscanned':
                    self.qy = self._read_blackboard(BlackboardDatumType.UNSCANNED_QUAD_Y)    
        if self.qx is None or self.qy is None:
            # We don't have target quadrant coordinates, so we cannot navigate
            startrek.print_strings(["NavigateToQuadrantAction Cannot navigate to quadrant: target coordinates not specified."])
            raise ActionCannotAchieveGoalError(action=self)

        # Make sure we aren't trying to navigate to the same quadrant
        assert(self._world.quadrant_x != self.qx or self._world.quadrant_y != self.qy)

        # Navigate to target quadrant
        print(f"NavigateToQuadrantAction Navigating to quadrant ({self.qx+1}, {self.qy+1}).")

        # Determine distance to target quadrant
        dist = startrek.distance(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
        # Determine direction to target quadrant
        direction = startrek.compute_direction(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
        # Perform navigation
        (output, obstacle) = startrek._navigation(direction, dist)
        startrek.print_strings(output)

        while obstacle:

            # Try to steer away from obstacle, by turning 45 degrees to the left, and navigating
            # 1 sector forward in that direction. 
            direction = float(StarTrekCourse(direction) + 1.0)  # Turn left by 45 degrees
            dist = 0.1 # A distance of 1 sector
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)
            assert(not obstacle)  # We should not hit an obstacle after turning left and moving forward.)

            # Now, reattempt navigation to the target quadrant.
            # Determine distance to target quadrant
            dist = startrek.distance(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
            # Determine direction to target quadrant
            direction = startrek.compute_direction(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
            # Perform navigation
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)

        return None

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
        
# TODO: Could consider breaking this apart into two actions. The first action would determine the direction.
# The second action would fire in that direction. And the two would be combined into a sequence to
# operationalize.
class LaunchPhotonTorpedoAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player launches a photon torpedo.
    """
    def __init__(self, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        Initialize the LaunchPhotonTorpedoAction object.
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
        Execute the launch photon torpedo action.
        :return: None
        """
        
        # Check if torpedo control is damaged or if we are out of torpedoes.
        (possible, output) = startrek._torpedo_control_precheck()
        if not possible:
            # Torpedo control is damaged, or we are out of torpedoes, and cannot launch a photon torpedo
            startrek.print_strings(output)
            return
        # Determine firing direction for torpedo
        target = self._world.klingon_ships[0]
        direction = startrek.compute_direction(self._world.sector_x, self._world.sector_y,
                                               target.sector_x, target.sector_y)
        print(f"LaunchPhotonTorpedoAction Launching photon torpedo at Klingon ship in sector ({target.sector_x+1},{target.sector_y+1}).")
        # Fire the torpedo
        output = startrek._torpedo_control_launch(direction)
        startrek.print_strings(output)
        self._is_complete = True
        return None

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        return self._is_complete

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with launching a photon torpedo.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with navigating to the target quadrant, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, DestroyKlingonShipGoal):
            # Not to be taken literally, but simply to indicated that completing this action
            # to lauch a photon torpedo will lower the insistence of the DestoryKlingonShipGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO