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
        self.deal_info = kwargs.get('action_type')
        self.go_play_score = kwargs.get('num_times')


