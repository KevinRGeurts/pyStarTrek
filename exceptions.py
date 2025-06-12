class GameAIError(Exception):
    """
    Base exception class for all custom exceptions specific to the Game AI foundation classes.
    """
    pass


class ExcessiveRepeatActionScheduleError(GameAIError):
    """
    Custom exception to be raised when the ActionManger is sequentially asked to schedule the same type of action too many times.
    This is a safeguard against potential infinite loops in the AI's action scheduling logic.
    Arguments expected in **kwargs:
        action_type: What type of GameAction was being scheduled repeatedly.
        num_times: An integer indicating how many times the action type was repeatedly scheduled.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._action_type = kwargs.get('action_type')
        self._num_times = kwargs.get('num_times')


class ActionCannotAchieveGoalError(GameAIError):
    """
    Custom exception to be raised when, while an action is executing, it is determined that the action
    cannot achieve the goal.
    Arguments expected in **kwargs:
        action: The GameAction that was executing.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._action = kwargs.get('action')
        self._parent_action = kwargs.get('parent_action', None)  # Optional parent action if this is a sub-action


