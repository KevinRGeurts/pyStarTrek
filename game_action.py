from game_goal import GameGoal, GoalInsistence


class GameAction(object):
    """
    This class represents a game action that can be performed by a player.
    """

    def __init__(self, expiry_time=0, priority=0):
        """
        :parameter expiry_time: The time in an arbitrary count-up from zero until the action expires, as int
        :parameter priority: The priority of the action. Higher numbers indicate higher priority. As int
        """
        self._expiry_time=expiry_time
        self._priority=priority

    @property
    def expiry_time(self):
        """
        Return the expiration time of the action. Expiration time is an arbitrary count-up from zero.
        :return: The expiration time of the action, as int.
        """
        return self._expiry_time

    @property
    def priority(self):
        """
        Return the priority of the action. Higher numbers indicate higher priority.
        :return: The priority of the action, as int.
        """
        return self._priority

    def canInterrupt(self):
        """
        Return whether this action can be interrupted by another action.
        :return: True if the action can be interrupted, False otherwise, as boolean.
        """
        # At this base class level, we assume that all actions cannot be interrupted.
        return False

    def canDoBoth(self, other_action):
        """
        Return whether this action can be done at the same time as another action.
        :param other_action: The other action to check against, as GameAction object.
        :return: True if both actions can be done at the same time, False otherwise, as boolean.
        """
        assert(isinstance(other_action, GameAction))
        # At this base class level, we assume that all actions cannot be done at the same time.
        return False

    def isComplete(self):
        """
        Return whether this action is complete.
        :return: True if the action is complete, False otherwise, as boolean.
        """
        # At this base class level, we assume that all actions are not complete.
        return False

    def execute(self):
        """
        Execute the action. This method should be overridden by subclasses to provide specific action behavior.
        :return: None
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with this action. This method should be overridden by subclasses to
            provide specific goal insistence change behavior.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with this action, as int.
        """
        assert(isinstance(goal, GameGoal))
        # By default, here in the base class, we assume that the action does not change any goal.
        return GoalInsistence.ZERO


class GameActionCombination(GameAction):
    """
    This class represents a combination of game actions that can be performed together.
    """
    def __init__(self, combo_acts=[]):
        """
        :parameter combo_acts: A list of GameAction objects that make up the combination.
        """
        super().__init__()
        self._action_list = [] # List of GameActions in the combination
        for act in combo_acts:
            assert(isinstance(act, GameAction))
            self._action_list.append(act)

    def canInterrupt(self):
        """
        Return whether this combination of actions can be interrupted by another action.
        :return: True if the combination of actions can be interrupted, False otherwise, as boolean.
        """
        # The combination can be interrupted if any of its subactions can be interrupted.
        for act in self._action_list:
            if act.canInterrupt():
                return True
        return False

    def canDoBoth(self, other_action):
        """
        Return whether this combination action can be done at the same time as another action.
        :param other_action: The other action to check against, as GameAction object.
        :return: True if both actions can be done at the same time, False otherwise, as boolean.
        """
        assert(isinstance(other_action, GameAction))
        # Combination is possible if it is possible for all subactions.
        for act in self._action_list:
            if not act.canDoBoth(other_action):
                return False
        return True

    def isComplete(self):
        """
        Return whether this combination action is complete.
        :return: True if the combination action is complete, False otherwise, as boolean.
        """
        # Combination is complete if all subactions are complete.
        for act in self._action_list:
            if not act.isComplete():
                return False
        return True

    def execute(self):
        """
        Execute all subactions in the combination.
        :return: None
        """
        for act in self._action_list:
            act.execute()

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with this combination action.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with this combination action, as int.
        """
        assert(isinstance(goal, GameGoal))
        # Add up the contributions of all subactions to the goal change, and return the negative of this total
        total = 0
        for act in self._action_list:
            total += act.getGoalChange(goal)
        return -total


class GameActionSequence(GameAction):
    """
    This class represents a sequence of game actions that must be performed in order.
    """
    def __init__(self, seq_acts=[]):
        """
        :parameter seq_acts: A list of GameAction objects that make up the ordered sequence.
        """
        super().__init__()
        self._action_list = [] # List of GameActions in the sequence
        for act in seq_acts:
            assert(isinstance(act, GameAction))
            self._action_list.append(act)
        self._activeIndex=0 # The index of the currently active (executing) action in the sequence

    def canInterrupt(self):
        """
        Return whether this sequence of actions can be interrupted by another action.
        :return: True if the sequence of actions can be interrupted, False otherwise, as boolean.
        """
        # The sequence can be interrupted if the active action can be interrupted. 
        return self._action_list[self._activeIndex].canInterrupt()

    def canDoBoth(self, other_action):
        """
        Return whether this sequence action can be done at the same time as another action.
        :param other_action: The other action to check against, as GameAction object.
        :return: True if both actions can be done at the same time, False otherwise, as boolean.
        """
        assert(isinstance(other_action, GameAction))
        # We can do both if all subactions that have not already been exectued can do both
        for i in range(self._activeIndex, len(self._action_list)):
            if not self._action_list[i].canDoBoth(other_action):
                return False
        return True

    def isComplete(self):
        """
        Return whether this sequence action is complete.
        :return: True if the sequence action is complete, False otherwise, as boolean.
        """
        #  Sequence is complete if all subactions are complete.
        return self._activeIndex >= len(self._action_list)

    def execute(self):
        """
        Execute subactions in the sequence one at a time and in order.
        :return: None
        """
        # Execute the current action in the sequence
        self._action_list[self._activeIndex].execute()

        # If current action is complete, move to the next action in the sequence
        if self._action_list[self._activeIndex].isComplete():
            self._activeIndex += 1

    def getGoalChange(self, goal=None):
        """
        Return the goal insistence change associated with this action sequence.
        :param goal: The goal to check against, as GameGoal object.
        :return: The goal insistence change associated with this action sequence, as int.
        """
        assert(isinstance(goal, GameGoal))
        # Add up the contributions of all subactions to the goal change, and return the negative of this total
        total = 0
        for act in self._action_list:
            total += act.getGoalChange(goal)
        return -total