"""
This module contains classes that represent dummy actions used to help test the ActionManager, GameActionCombination,
and GameActionSequence classes.
"""


# standard imports

# local imports
from game_action import GameAction

class dummyAction(GameAction):
    """
    This class represents a dummy action used to help test the ActionManager.
    """
    def __init__(self, expiry_time=0, priority=0):
        """
        :parameter expiry_time: The time in an arbitrary count-up from zero until the action expires, as int
        :parameter priority: The priority of the action. Higher numbers indicate higher priority. As int
        """
        super().__init__(expiry_time, priority)
        self._canInterrupt = False
        self._canDoBoth = False

    def canInterrupt(self):
        """
        Return whether this action can be interrupted by another action.
        :return: True if the action can be interrupted, False otherwise, as boolean.
        """
        return self._canInterrupt

    def canDoBoth(self, other_action):
        """
        Return whether this action can be done at the same time as another action.
        :param other_action: The other action to check against, as GameAction object.
        :return: True if both actions can be done at the same time, False otherwise, as boolean.
        """
        assert(isinstance(other_action, GameAction))
        return self._canDoBoth

    def execute(self):
        """
        Execute the action. In this case, simply by setting the completed flag to True.
        :return: None
        """
        self._completed = True
        return None


