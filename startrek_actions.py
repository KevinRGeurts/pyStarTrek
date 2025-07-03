# standard imports
from enum import StrEnum

# local imports
from math import exp
from game_action import GameAction, GameActionSequence
from game_goal import GameGoal, GoalInsistence
from startrek_goals import DestroyKlingonShipGoal, ExploreGalaxyGoal, SurviveGoal, FindKlingonShipGoal
from startrek_goals import RepairResuplyEnterpriseGoal, ABSOLUTE_MINIMUM_SHIP_ENERGY
from utilities import StarTrekCourse
from world_interface import WorldInterface
from exceptions import ActionCannotAchieveGoalError
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class BlackboardDatumType(StrEnum):
    """
    Enumeration of the types of data that can be written to the blackboard in a Star Trek game.
    """
    KLINGON_QUAD_X = 'klingon_quad_x' # The x-coordinate of a quadrant with Klingon ship(s) [0..7], as int.
    KLINGON_QUAD_Y = 'klingon_quad_y' # The y-coordinate of a quadrant with Klingon ship(s) [0..7], as int.
    BASE_QUAD_X = 'base_quad_x' # The x-coordinate of a quadrant with a starbase [0..7], as int.
    BASE_QUAD_Y = 'base_quad_y' # The y-coordinate of a quadrant with a starbase [0..7], as int.
    BASE_SECT_X = 'base_sect_x' # The x-coordinate of a sector with a starbase [0..7], as int.
    BASE_SECT_Y = 'base_sect_y' # The y-coordinate of a sector with a starbase [0..7], as int.
    EMPT_SECT_X = 'empty_sect_x' # The x-coordinate of an empty sector within a quadrant [0..7], as int.
    EMPT_SECT_Y = 'empty_sect_y' # The y-coordinate of an empty sector within a quadrant [0..7], as int.
    UNSCANNED_QUAD_X = 'unscanned_quad_x' # The x-coordinate of an unscanned quadrant [0..7], as int.
    UNSCANNED_QUAD_Y = 'unscanned_quad_y' # The y-coordinate of an unscanned quadrant [0..7], as int.
    FIRE_PHASERS = 'fire_phasers' # Whether to fire phasers, as boolean.
    SUGGESTED_PHASER_LEVEL = 'suggested_phaser_level' # The suggested phaser energy level to fire at, as int.


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


class FindStarbaseAction(GameActionSequence):
    """
    Represents a sequence of actions in a Star Trek game where a player scans and checks the galactic record
    to find a quadrant with a starbase, and then navigates to that quadrant. Then a short range scan is
    performed to find the starbase, and then the Enterprise is navigated to dock with the starbase.
    :param expiry_time: The time in an arbitrary count-up from zero until the action sequence expires, as int.
    :param priority: The priority of the action sequence. Higher numbers indicate higher priority. As int.
    """
    def __init__(self, expiry_time=0, priority=0):
        long_scan_act = LongRangeScanAction(read_blackboard=self.readFromBlackBoard,
                                       write_blackboard=self.writeToBlackBoard)
        rec_act = CheckGalacticRecordAction(read_blackboard=self.readFromBlackBoard,
                                            write_blackboard=self.writeToBlackBoard)
        nav_act = NavigateToQuadrantAction(looking_for='starbase',
                                           read_blackboard=self.readFromBlackBoard,
                                           write_blackboard=self.writeToBlackBoard)
        short_scan_act = ShortRangeScanAction(read_blackboard=self.readFromBlackBoard,
                                              write_blackboard=self.writeToBlackBoard)
        dock_act = DockWithStarbaseAction(read_blackboard=self.readFromBlackBoard,
                                          write_blackboard=self.writeToBlackBoard)
        undock_act = UndockFromStarbaseAction(read_blackboard=self.readFromBlackBoard,
                                            write_blackboard=self.writeToBlackBoard)
        super().__init__(expiry_time, priority, seq_acts=[long_scan_act, rec_act, nav_act, short_scan_act, dock_act, undock_act])


class AttackKlingonShipAction(GameActionSequence):
    """
    Represents a sequence of actions in a Star Trek game where a player attacks a Klingon ship.
    :param expiry_time: The time in an arbitrary count-up from zero until the action sequence expires, as int.
    :param priority: The priority of the action sequence. Higher numbers indicate higher priority. As int.
    """
    def __init__(self, expiry_time=0, priority=0):
        torp_act = LaunchPhotonTorpedoAction(read_blackboard=self.readFromBlackBoard,
                                             write_blackboard=self.writeToBlackBoard)
        phas_act = FirePhasersAction(phaser_energy=500,
                                     read_blackboard=self.readFromBlackBoard,
                                     write_blackboard=self.writeToBlackBoard)
        super().__init__(expiry_time, priority, seq_acts=[torp_act, phas_act])


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


class ShortRangeScanAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player performs a short-range scan of the quadrant
    with intent to find a Starbase.
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
        Execute the short range scan action.
        :return: None
        """
        if self._world.short_range_scan_damage > 0:
            # Short range scanner is damaged, and cannot be used
            startrek.print_strings(["Short range scanner is damaged, and cannot be used."])
            return

        # Just fetch the starbase location directly from the world interface.
        base_sect_x = -1
        base_sect_y = -1

        try:
            base_sect_x = self._world.starbase_x 
            base_sect_y = self._world.starbase_y
        except AssertionError:
            # No starbase in the current quadrant, so no coordinates to write to blackboard.
            pass

        # Write starbase coordinates to blackboard, if we have one
        if base_sect_x >= 0 and base_sect_y >= 0:
            print(f"ShortRangeScanAction found starbase at quadrant ({base_sect_x+1}, {base_sect_y+1}).")
            if self._write_blackboard is not None:
                self._write_blackboard(BlackboardDatumType.BASE_SECT_X, base_sect_x)
                self._write_blackboard(BlackboardDatumType.BASE_SECT_Y, base_sect_y)
        
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
        if isinstance(goal, RepairResuplyEnterpriseGoal):
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
            if (self._world.energy - (self._shield_energy - current_shields)) < ABSOLUTE_MINIMUM_SHIP_ENERGY:
                # Not enough energy to raise shields, while maintaining a mimumum level of ship's energy
                startrek.print_strings([f"Not enough energy to increase shields to {self._shield_energy}."])
                startrek.print_strings([f"Minimum ship energy is {ABSOLUTE_MINIMUM_SHIP_ENERGY}."])
                available_energy = self._world.energy - ABSOLUTE_MINIMUM_SHIP_ENERGY
                if available_energy > 0:
                    startrek.print_strings([f"Shields will be increased to {current_shields + available_energy}."])
                    self._shield_energy = available_energy
                else:
                    return
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
            print(f"NavigateToQuadrantAction Navigating around obstacle near ({self._world.sector_x+1}, {self._world.sector_x+1}).")
            # Try to steer around the obstacle.
            # First, back up a bit, by turning 180 degrees. 
            direction = float(StarTrekCourse(direction) - 4.0)  # Turn by 180 degrees
            dist = 1.0 / 8.0 # A distance of 1 sector
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)
            assert(not obstacle)  # We should not hit an obstacle by backing up.
            # Now reorient so we are 45 degrees right of the course that oringinally took us to the obstacle.
            direction = float(StarTrekCourse(direction) + 3.0)  # Turn back by 180-45 = 135 degrees
            dist = 2.0 / 8.0 # A distance of 2 sectors, hopefully enough to get around the obstacle.
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)
            assert(not obstacle)  # We should not hit an obstacle by this turning back maneuver.
            
            # Now next attempt to navigate to the target quadrant will be left to the next
            # invocation of the execute() method.
            
            # # Now, reattempt navigation to the target quadrant.
            # # Determine distance to target quadrant
            # dist = startrek.distance(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
            # # Determine direction to target quadrant
            # direction = startrek.compute_direction(self._world.quadrant_x, self._world.quadrant_y, self.qx, self.qy)
            # # Perform navigation
            # (output, obstacle) = startrek._navigation(direction, dist)
            # startrek.print_strings(output)

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
        
        # Note: We will mark the action complete, if and only if:
        # (1) We launch a torpoedo that does not miss, or
        # (2) We can't launch a torpedo, but we can write to the blackboard that phasers should be fired.
        # We do not want to mark the action complete if we launched a torpedo which simply missed, since that
        # can happen with random chance, and we want to try launching a torpedo again. 

        # Check if torpedo control is damaged or if we are out of torpedoes.
        (possible, output) = startrek._torpedo_control_precheck()
        if not possible:
            # Torpedo control is damaged, or we are out of torpedoes, and cannot launch a photon torpedo
            startrek.print_strings(output)
            if self._write_blackboard is not None:
                # If we can't launch a photon torpedo, write to the blackboard that phasers should be fired.
                self._write_blackboard(BlackboardDatumType.FIRE_PHASERS, True)
                self._is_complete = True
            return
        # Determine firing direction for torpedo
        target = self._world.klingon_ships[0]
        direction = startrek.compute_direction(self._world.sector_x, self._world.sector_y,
                                               target.sector_x, target.sector_y)
        print(f"LaunchPhotonTorpedoAction Launching photon torpedo at Klingon ship in sector ({target.sector_x+1},{target.sector_y+1}).")
        # Fire the torpedo
        (output, captured, missed) = startrek._torpedo_control_launch(direction)
        if not missed:
            self._is_complete = True
        startrek.print_strings(output)
        if self._write_blackboard is not None:
            # If the torpedo was captured by a star, write to the blackboard that phasers should be fired.
            self._write_blackboard(BlackboardDatumType.FIRE_PHASERS, captured)
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


class FirePhasersAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player fires phasers.
    """
    def __init__(self, phaser_energy=0, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        Initialize the fire phasers action object.
        :param phaser_energy: The desired energy level for the phasers, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        self._phaser_energy = phaser_energy
        self._is_complete = False

    def execute(self):
        """
        Execute the fire phasers action.
        :return: None
        """

        if self._read_blackboard is not None:
            if not self._read_blackboard(BlackboardDatumType.FIRE_PHASERS):
                # If the blackboard indicates that we should not fire phasers, then we do not.
                self._is_complete = True
                print("FirePhasersAction Not firing phasers: blackboard indicates not to fire.")
                return
            
            suggested_phaser_level = self._read_blackboard(BlackboardDatumType.SUGGESTED_PHASER_LEVEL)
            if suggested_phaser_level is not None:
                # If the blackboard suggests a phaser energy level, then use that instead of the one specified in the action.
                self._phaser_energy = suggested_phaser_level
                print(f"FirePhasersAction Using suggested phaser energy level of {self._phaser_energy}.")
            
        # Check if phaser control is damaged or if we are out of torpedoes.
        (possible, output) = startrek._phaser_control_precheck()
        if not possible:
            # Phaser control is damaged. Phasers cannot be fired.
            startrek.print_strings(output)
            return
        # Determine how many Klingon ships are in the current quadrant
        num_targets = len(self._world.klingon_ships)
        print(f"FirePhasersAction Firing phasers with energy level {self._phaser_energy} at {num_targets} Klingon ships in quadrant.")
        # Fire the phasers
        (output, num_destroyed, remaining_ships) = startrek._phaser_controls_fire(self._phaser_energy)
        startrek.print_strings(output)
        if num_destroyed >= num_targets:
            # If we destroyed all targets, then the action is complete.
            self._is_complete = True
        else:
            # If we did not destroy all targets, write a hint to the blackboard of the phaser energy to use
            # the next time we fire phaseers.
            max_phaser_energy_needed = 0
            for ship in remaining_ships:
                energy_needed = ship[1] / (1.0 - ship[0]/11.3) # Magic number of 11.3 comes from the startrek module _phaser_controls_fire(...)
                if energy_needed > max_phaser_energy_needed:
                    max_phaser_energy_needed = energy_needed
            max_phaser_energy_needed = len(remaining_ships) * max_phaser_energy_needed  # Total energy needed to destroy all remaining ships)
            if self._write_blackboard is not None:
                self._write_blackboard(BlackboardDatumType.SUGGESTED_PHASER_LEVEL, max_phaser_energy_needed)
        return None

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        return self._is_complete

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with firing phasers.
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


class DockWithStarbaseAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player navigates within a sector to dock with a starbase.
    """
    def __init__(self, sx=None, sy=None, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :param sx: The sector x-coordinate [0..7] to navigate to, as int.
        :param sy: The sector y-coordinate [0..7] to navigate to, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        if sx is not None: assert(sx>=0 and sx<=7)
        self.sx = sx
        if sy is not None: assert(sy>=0 and sy<=7)
        self.sy = sy
        # How many times have we attempted to navigate to the target sector?
        self._attempts = 0
        self._max_attempts = 2  # If we attempt to navigate to the same sector too many times, we'll give up.

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        # Check if the current game sector matches the target sector, or if we are docked with starbase.
        # If either is so, then navigation was successful, and the action is complete. Note that docking with
        # starbase halts Enterprise at an adjacent sector, not at the starbase sector.
        if self._world.sector_x == self.sx and self._world.sector_y == self.sy:
            # Navigation was successful
            return True
        elif self._world.docked:
            # We are docked with the starbase, so we are done.
            return True
        elif self._attempts > self._max_attempts:
            # If we have attempted to navigate to the target sector too many times, then we give up.
            startrek.print_strings(["DockWithStarbaseAction failed: too many attempts to navigate to the same sector."])
            return True
        else:
            return False

    def execute(self):
        """
        Execute the navigation action.
        :return: None
        """

        self._attempts += 1

        # If we don't have target sector coordinates, then we need to read them from the blackboard.
        if self.sx is None:
            assert(self._read_blackboard is not None)
            self.sx = self._read_blackboard(BlackboardDatumType.BASE_SECT_X)    
        if self.sy is None:
            assert(self._read_blackboard is not None)
            self.sy = self._read_blackboard(BlackboardDatumType.BASE_SECT_Y)    
        if self.sx is None or self.sy is None:
            # We don't have target sector coordinates, so we cannot navigate
            startrek.print_strings(["DockWithStarbaseAction Cannot navigate to sector: target coordinates not specified."])
            raise ActionCannotAchieveGoalError(action=self)

        # Make sure we aren't trying to navigate to the same sector
        assert(self._world.sector_x != self.sx or self._world.sector_y != self.sy)

        # Navigate to target sector
        print(f"DockWithStarbaseAction Navigating to sector ({self.sx+1}, {self.sy+1}).")

        # Determine distance to target sector
        dist = startrek.distance(self._world.sector_x, self._world.sector_y, self.sx, self.sy) / 8.0
        # Determine direction to target sector
        direction = startrek.compute_direction(self._world.sector_x, self._world.sector_y, self.sx, self.sy)
        # Perform navigation
        self.writeLastSector(self._world.sector_x, self._world.sector_y)
        (output, obstacle) = startrek._navigation(direction, dist)
        startrek.print_strings(output)

        while obstacle and not self._world.docked:
            print(f"DockWithStarbaseAction Navigating around obstacle near ({self._world.sector_x+1}, {self._world.sector_x+1}).")
            # Try to steer around the obstacle.
            # First, back up a bit, by turning 180 degrees.
            direction = float(StarTrekCourse(direction) - 4.0)  # Turn by 180 degrees
            dist = 1.0 / 8.0 # A distance of 1 sector
            self.writeLastSector(self._world.sector_x, self._world.sector_y)
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)
            assert(not obstacle)  # We should not hit an obstacle by backing up.
            # Now reorient so we are 45 degrees right of the course that oringinally took us to the obstacle.
            direction = float(StarTrekCourse(direction) + 3.0)  # Turn back by 180-45 = 135 degrees
            dist = 2.0 / 8.0 # A distance of 2 sectors, hopefully enough to get around the obstacle.
            self.writeLastSector(self._world.sector_x, self._world.sector_y)
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)
            assert(not obstacle)  # We should not hit an obstacle by this turnning back maneuver.
            # Now, reattempt navigation to the target sector.
            # Determine distance to target sector
            dist = startrek.distance(self._world.sector_x, self._world.sector_y, self.sx, self.sy) / 8.0
            # Determine direction to target sector
            direction = startrek.compute_direction(self._world.sector_x, self._world.sector_y, self.sx, self.sy)
            # Perform navigation
            self.writeLastSector(self._world.sector_x, self._world.sector_y)
            (output, obstacle) = startrek._navigation(direction, dist)
            startrek.print_strings(output)

        return None

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with navigating to the target sector.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with navigating to the target sector, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, RepairResuplyEnterpriseGoal):
            # Not to be taken literally, but simply to indicated that completing this action
            # to dock with a starbase will lower the insistence of the RepairResuplyEnterpriseGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO

    def writeLastSector(self, sx=None, sy=None):
        """
        Write to the blackboard the last sector the Enterprise navigated from before successfully docking with a starbase.
        :param sx: The sector x-coordinate [0..7] to write, as int.
        :param sy: The sector y-coordinate [0..7] to write, as int.
        :return: None
        """
        if self._write_blackboard is not None:
            self._write_blackboard(BlackboardDatumType.EMPT_SECT_X, sx)
            self._write_blackboard(BlackboardDatumType.EMPT_SECT_Y, sy)
        return None


class UndockFromStarbaseAction(StarTrekAction):
    """
    Represents an action in a Star Trek game where a player navigates within a sector to undock from a starbase.
    """
    def __init__(self, sx=None, sy=None, expiry_time=0, priority=0, read_blackboard=None, write_blackboard=None):
        """
        :param sx: The sector x-coordinate [0..7] to navigate to, as int.
        :param sy: The sector y-coordinate [0..7] to navigate to, as int.
        :param expiry_time: The time in an arbitrary count-up from zero until the action expires, as int.
        :param priority: The priority of the action. Higher numbers indicate higher priority. As int.
        :parameter read_blackboard: A function to read from the blackboard, as callable
            Signature: read_blackboard(key: str) -> any
        :parameter write_blackboard: A function to write to the blackboard, as callable
            Signature: write_blackboard(key: str, value: any) -> None
        """
        super().__init__(expiry_time, priority, read_blackboard, write_blackboard)
        if sx is not None: assert(sx>=0 and sx<=7)
        self.sx = sx
        if sy is not None: assert(sy>=0 and sy<=7)
        self.sy = sy
        # How many times have we attempted to navigate to the target sector?
        self._attempts = 0
        self._max_attempts = 2  # If we attempt to navigate to the same sector too many times, we'll give up.

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        # Check if the current game sector matches the target sector, and if we are not docked with starbase.
        if self._world.sector_x == self.sx and self._world.sector_y == self.sy and not self._world.docked:
            # Navigation was successful
            return True
        elif self._attempts > self._max_attempts:
            # If we have attempted to navigate to the target sector too many times, then we give up.
            startrek.print_strings(["UndockFromStarbaseAction failed: too many attempts to navigate to the same sector."])
            return True
        else:
            return False

    def execute(self):
        """
        Execute the navigation action.
        :return: None
        """

        self._attempts += 1

        # If we don't have target sector coordinates, then we need to read them from the blackboard.
        if self.sx is None:
            assert(self._read_blackboard is not None)
            self.sx = self._read_blackboard(BlackboardDatumType.EMPT_SECT_X)    
        if self.sy is None:
            assert(self._read_blackboard is not None)
            self.sy = self._read_blackboard(BlackboardDatumType.EMPT_SECT_Y)    
        if self.sx is None or self.sy is None:
            # We don't have target sector coordinates, so we cannot navigate
            startrek.print_strings(["UndockFromStarbaseAction Cannot navigate to sector: target coordinates not specified."])
            raise ActionCannotAchieveGoalError(action=self)

        # Make sure we aren't trying to navigate to the same sector
        assert(self._world.sector_x != self.sx or self._world.sector_y != self.sy)

        # Navigate to target sector
        print(f"UndockFromStarbaseAction Navigating to sector ({self.sx+1}, {self.sy+1}).")

        # Determine distance to target sector
        dist = startrek.distance(self._world.sector_x, self._world.sector_y, self.sx, self.sy) / 8.0
        # Determine direction to target sector
        direction = startrek.compute_direction(self._world.sector_x, self._world.sector_y, self.sx, self.sy)
        # Perform navigation
        (output, obstacle) = startrek._navigation(direction, dist)
        startrek.print_strings(output)
        assert(not obstacle)  # We should not hit an obstacle moving to an empty sector near a starbase.

        return None

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with navigating to the target sector.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with navigating to the target sector, as int.
        """
        assert(isinstance(goal, GameGoal))
        if isinstance(goal, RepairResuplyEnterpriseGoal):
            # Not to be taken literally, but simply to indicated that completing this action
            # to undock from a starbase (after docking) will lower the insistence of the RepairResuplyEnterpriseGoal.
            return -GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO
