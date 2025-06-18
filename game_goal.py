# standard imports
from enum import IntEnum

# local imports

class GoalInsistence(IntEnum):
    """
    This class represents the insistence values of goals in a goal-oriented behavior (GOB) system for decision making by game AI.
    """
    ZERO = 0
    LOW = 2
    MEDIUM = 4
    HIGH = 8
    VERY_HIGH = 16
    URGENT = 32


class GameGoal(object):
    """
    This class represents a goal within a goal-oriented behavior (GOB) system for decicion making by game AI.
    """
    def __init__(self, name='a goal'):
        """
        :parameter name: The name of the goal, as string.
        """
        self._name=name

    @property
    def name(self):
        """
        Return the name of the goal.
        :return: The name of the goal, as string.
        """
        return self._name

    def __str__(self):
        """
        Return the string representation of the goal.
        :return: The string representation of the goal, as string.
        """
        return f"Goal: {self._name}"

    def getInsistence(self):
        """
        Return the insistence value of the goal. This method should be overridden by subclasses to provide specific goal behavior.
        :return: The insistence value of the goal, int
        """
        raise NotImplementedError("Subclasses must implement this method.")


