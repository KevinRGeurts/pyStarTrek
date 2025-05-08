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
        self._completed=False

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
        return self._completed

    def execute(self):
        """
        Execute the action. This method should be overridden by subclasses to provide specific action behavior.
        :return: None
        """
        raise NotImplementedError("Subclasses must implement this method.")


