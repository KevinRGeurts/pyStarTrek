class StarTrekError(Exception):
    """
    Base exception class for all custom exceptions specific to the Star Trek game.
    """
    pass


# TODO: Consider if this is actually required.
class EncounteredObstacleInQuadrantError(StarTrekError):
    """
    Custom exception to be raised when the encountering an obstacle in a quadrant while navigating.
    Arguments expected in **kwargs:
        obstacle_x: The x-coordinate (sector) of the obstacle in the quadrant, as int [0-7].
        obstacle_y: The y-coordinate (sector) of the obstacle in the quadrant, as int [0-7].
        sector_type: What type of obstacle was encountered, as int, as defined by SectorType class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._obstacle_x = kwargs.get('obstacle_x')
        self._obstacle_y = kwargs.get('obstacle_y')
        self._sector_type = kwargs.get('sector_type')


