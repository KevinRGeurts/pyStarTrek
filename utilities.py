"""
This module contains utility functions for the Star Trek game.
"""

# standard imports
from math import atan2, pi, sqrt

# local imports


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