"""
This module contains utility functions for the Star Trek game.
"""

# standard imports
from math import atan2, pi, sqrt

# local imports


def print_strings(string_list):
    for string in string_list:
        print(string)
    print


def compute_direction(x1, y1, x2, y2):
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
    x = x2 - x1
    y = y2 - y1
    return sqrt(x * x + y * y)


def input_double(prompt):
    text = input(prompt)
    try:
        value = float(text)
        return value
    except: # Most likely a ValueError
        return False