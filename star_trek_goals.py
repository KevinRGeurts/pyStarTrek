# standard imports

# local imports
from game_goal import GameGoal, GoalInsistence
from world_interface import WorldInterface

class SurviveGoal(GameGoal):
    """
    This class represents the goal in a Star Trek game for the Enterprise to survive the game.
    """
    def __init__(self):
        """
        Initialize the SurviveGoal object.
        """
        super().__init__(name="Survive")
        self._world=WorldInterface()

    def getInsistence(self):
        """
        Return the insistence value of the Survive goal.
        :return: The insistence of the Survive goal, as int
        """
        if self._world.shields <= 0 and self._world.quadrant.klingons > 0:
            return GoalInsistence.URGENT
        else:
            return GoalInsistence.ZERO


class FindKlingonShipGoal(GameGoal):
    """
    This class represents the goal in a Star Trek game for the Enterprise find a Klingon ship to attack.
    """
    def __init__(self):
        """
        Initialize the FindKlingonShipGoal object.
        """
        super().__init__(name="FindKlingonShip")
        self._world=WorldInterface()

    def getInsistence(self):
        """
        Return the insistence value of the Survive goal.
        :return: The insistence of the Survive goal, as int
        """
        if self._world.quadrant.klingons > 0:
            return GoalInsistence.ZERO
        elif (False):
            # 
            return GoalInsistence.ZERO



