# standard imports
from copy import deepcopy

# local imports
from game_goal import GameGoal
from game_action import GameAction


class Gob(object):
    """
    This class implements goal-oriented behavior.
    """
    def __init__(self):
        """
        Initialize the gob object.
        """
        self._goals = []
        self._actions = []

    def add_goal(self, goal):
        """
        Add a goal to the gob object.
        :param goal: The goal to be added, as an instance of GameGoal.
        :return: None
        """
        assert(isinstance(goal, GameGoal))
        self._goals.append(goal)
        return None

    def remove_goal(self, goal):
        """
        Remove a goal from the gob object.
        :param goal: The goal to be removed, as an instance of GameGoal.
        :return: None
        """
        assert(isinstance(goal, GameGoal))
        try:
            self._goals.remove(goal)
        except ValueError:
            print(f"Goal {goal.name} not found in the list of goals.")
        return None

    def add_action(self, action):
        """
        Add an action to the gob object.
        :param action: The action to be added, as an instance of GameAction.
        :return: None
        """
        assert(isinstance(action, GameAction))
        self._actions.append(action)
        return None

    def remove_action(self, action):
        """
        Remove an action from the gob object.
        :param action: The action to be removed, as an instance of GameAction.
        :return: None
        """
        assert(isinstance(action, GameAction))
        try:
            self._actions.remove(action)
        except ValueError:
            print(f"Action {action} not found in the list of actions.")
        return None

    def chooseAction(self):
        """
        Choose the best action based on the current goals and actions.
        :return: The chosen action, as an instance of GameAction, or None if no action is chosen.
            Note that the action returned will be a deep copy of the original action. That is, 
            self._actions is treated as a list of prototypes.
        """
        # Find the goal to try and fulfill
        topGoal = self._goals[0]
        for goal in self._goals[1:]:
            if goal.getInsistence() > topGoal.getInsistence():
                topGoal = goal

        # Find the best action to fulfill the top goal
        bestAction = self._actions[0]
        # Invert the change because a low change value is good
        bestUtility = -bestAction.getGoalChange(topGoal)
        for action in self._actions[1:]:
            utility = -action.getGoalChange(topGoal)
            # We look for the lowest change, or the highest utility
            if utility > bestUtility:
                bestAction = action
                bestUtility = utility

        return deepcopy(bestAction)


