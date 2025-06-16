"""
This module contains utility functions for the Star Trek game.
"""

# standard imports
from math import atan2, pi, sqrt

# local imports


class StarTrekCourse:
    """
    This class represents a course (direction) in the Star Trek game.
    Note: Course is defined as follows: [1.0-9.0], 1=right,3=up,5=left,7=down
    """
    def __init__(self, direction=1.0):
        """
        :parameter direction: The direction of the course, as float.
        Note: Direction is defined as follows: [1.0-9.0], 1=right,3=up,5=left,7=down
        """
        self.direction = direction

    @property
    def direction(self):
        """
        Get the direction of the course.
        :return: The direction as a float
        Note: Direction is defined as follows: [1.0-9.0], 1=right,3=up,5=left,7=down
        """
        return self._direction

    @direction.setter
    def direction(self, direction):
        """
        Set the direction of the course.
        :parameter direction: The direction of the course, as float.
        Note: Direction is defined as follows: [1.0-9.0], 1=right,3=up,5=left,7=down
        """
        assert(1.0 <= direction <= 9.0)
        self._direction = direction

    def __repr__(self):
        return f"StarTrekCourse(direction={self.direction})"

    def __str__(self):
        return str(float(self.direction))
        
    def __int__(self):
        return int(self.direction)

    def __float__(self):
        return float(self.direction)

    def __add__(self, other):
        if not isinstance(other, (StarTrekCourse, float, int)):
            return NotImplemented
        result = float(self) + float(other)
        if result > 9.0:
            result -= 9.0 
        return StarTrekCourse(result)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if not isinstance(other, (StarTrekCourse, float, int)):
            return NotImplemented
        result = float(self) - float(other)
        if result <= 1.0:
            result = 8.0 + result 
        return StarTrekCourse(result)

    def __rsub__(self, other):
        return self.__sub__(other)


def print_strings(string_list):
    """
    Iterate through a list of strings and print each string.
    """
    for string in string_list:
        print(string)
    print


def compute_direction(x1, y1, x2, y2):
    """
    Compute the direction from one point to another in a 2D space.
    :parameter x1: The x-coordinate of the first point, float or int
    :parameter y1: The y-coordinate of the first point, float or int
    :parameter x2: The x-coordinate of the second point, float or int
    :parameter y2: The y-coordinate of the second point, float or int
    :return: The direction from the first point to the second point, as a float
    """
    if x1 == x2:
        if y1 < y2:
            direction = 7
        else:
            direction = 3
    elif y1 == y2:
        if x1 < x2:
            direction = 1
        else:
            direction = 5
    else:
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        angle = atan2(dy, dx)
        if x1 < x2:
            if y1 < y2:
                direction = 9.0 - 4.0 * angle / pi
            else:
                direction = 1.0 + 4.0 * angle / pi
        else:
            if y1 < y2:
                direction = 5.0 + 4.0 * angle / pi
            else:
                direction = 5.0 - 4.0 * angle / pi
    return direction


def distance(x1, y1, x2, y2):
    """
    Compute the distance between two points in a 2D space.
    :parameter x1: The x-coordinate of the first point, float or int
    :parameter y1: The y-coordinate of the first point, float or int
    :parameter x2: The x-coordinate of the second point, float or int
    :parameter y2: The y-coordinate of the second point, float or int
    :return: The distance between the two points, as a float
    """
    x = x2 - x1
    y = y2 - y1
    return sqrt(x * x + y * y)


def input_double(prompt):
    """
    Prompt the user for a floating-point number and return it.
    :parameter prompt: The prompt to display to the user, as a string
    :return: The floating-point number entered by the user, or False if the input is invalid
    """
    text = input(prompt)
    try:
        value = float(text)
        return value
    except: # Most likely a ValueError
        return False