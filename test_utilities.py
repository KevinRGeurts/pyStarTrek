# standard imports
import unittest
from io import StringIO
from unittest.mock import patch
import sys

# local imports
from utilities import input_double, print_strings, compute_direction, distance, input_double
from strings import computerStrings


class Test_utilities(unittest.TestCase):
    def test_print_strings(self):
        exp_val='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Print the string
        print_strings(computerStrings)
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_compute_direction(self):
        # x1=x2, y1<y2
        exp_val=7
        act_val=compute_direction(2,5,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1=x2, y1>y2
        exp_val=3
        act_val=compute_direction(2,7,2,5)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1=y2
        exp_val=1
        act_val=compute_direction(2,7,4,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1=y2
        exp_val=5
        act_val=compute_direction(4,7,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1<y2
        exp_val=6
        act_val=compute_direction(4,5,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1>y2
        exp_val=4
        act_val=compute_direction(4,7,2,5)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1<y2
        exp_val=8
        act_val=compute_direction(2,5,4,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1>y2
        exp_val=2
        act_val=compute_direction(2,7,4,5)
        self.assertAlmostEqual(exp_val, act_val)

    def test_distance(self):
        exp_val=7.071067812
        act_val=distance(2,3,7,8)
        self.assertAlmostEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in valid input of a float
    @patch('sys.stdin', StringIO('7.56\n'))
    def test_input_double(self):
        exp_val=7.56
        act_val=input_double('Enter a valid floating point number:')
        self.assertAlmostEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in invalid input
    @patch('sys.stdin', StringIO('foo\n'))
    def test_input_double_invalid(self):
        act_val=input_double('Enter a valid floating point number:')
        self.assertFalse(act_val)


if __name__ == '__main__':
    unittest.main()
