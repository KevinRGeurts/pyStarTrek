# standard imports

# local imports
from game_goal import GameGoal, GoalInsistence
from world_interface import WorldInterface


class RepairResuplyEnterpriseGoal(GameGoal):
    """
    This class represents the goal in a Star Trek game for the Enterprise to repair and resupply itself.
    """
    def __init__(self):
        """
        Initialize the RepairResuplyEnterpriseGoal object.
        """
        super().__init__(name="RepairResuplyEnterprise")
        self._world=WorldInterface()

    def getInsistence(self):
        """
        Return the insistence value of the RepairResuplyEnterprise goal.
        :return: The insistence of the RepairResuplyEnterprise goal, as int
        """
        # TODO: Also check for damage to the Enterprise
        if self._world.energy < 500:
            return GoalInsistence.VERY_HIGH
        elif self._world.photon_torpedoes < 1:
            return GoalInsistence.VERY_HIGH
        elif self._world.phaser_damage and self._world.photon_torpedo_damage > 0:
            return GoalInsistence.VERY_HIGH
        elif self._world.shield_control_damage > 0:
            return GoalInsistence.VERY_HIGH
        else:
            return GoalInsistence.ZERO


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
        if self._world.shield_level <= 100 and self._world.quadrant.klingons > 0:
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
        Return the insistence value of the FindKlingonShip goal.
        :return: The insistence of the FindKlingonShip goal, as int
        """
        if self._world.quadrant.klingons <= 0:
            return GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO


class DestroyKlingonShipGoal(GameGoal):
    """
    This class represents the goal in a Star Trek game for the Enterprise to destroy a Klingon ship.
    """
    def __init__(self):
        """
        Initialize the DestroyKlingonShip object.
        """
        super().__init__(name="DestroyKlingonShip")
        self._world=WorldInterface()

    def getInsistence(self):
        """
        Return the insistence value of the DestroyKlingonShip goal.
        :return: The insistence of the DestroyKlingonShip goal, as int
        """
        if self._world.quadrant.klingons > 0:
            return GoalInsistence.HIGH
        else:
            return GoalInsistence.ZERO


class ExploreGalaxyGoal(GameGoal):
    """
    This class represents the goal in a Star Trek game for the Enterprise to explore the (unscanned) galaxy.
    """
    def __init__(self):
        """
        Initialize the ExploreGalaxyGoal object.
        """
        super().__init__(name="ExploreGalaxy")
        self._world=WorldInterface()

    def getInsistence(self):
        """
        Return the insistence value of the ExploreGalaxy goal.
        :return: The insistence of the ExploreGalaxy goal, as int
        """
        if self._world.quadrant.klingons <= 0:
            return GoalInsistence.MEDIUM
        else:
            return GoalInsistence.ZERO
