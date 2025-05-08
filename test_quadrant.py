# standard imports
import unittest

# local imports
from quadrant import Quadrant


class Test_Quadrant(unittest.TestCase):
    def test_Quadrant_init(self):
        quad = Quadrant()
        exp_val=('', 0, 0, False, False)
        act_val=(quad.name, quad.klingons, quad.stars, quad.starbase, quad.scanned)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
