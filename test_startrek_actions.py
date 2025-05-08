# standard imports
import unittest
import random

# local imports
import startrek_actions  # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.

class Test_NavigateToQuadrantAction(unittest.TestCase):
    def test_init(self):
        act=startrek_actions.NavigateToQuadrantAction(qx=7, qy=2, expiry_time=3, priority=10)
        exp_val = (7, 2, 3, 10)
        act_val = (act.qx, act.qy, act.expiry_time, act.priority)
        self.assertTupleEqual(exp_val, act_val)

    def test_init_qx_low(self):
        self.assertRaises(AssertionError, startrek_actions.NavigateToQuadrantAction,
                          qx=-1, qy=2, expiry_time=3, priority=10)

    def test_init_qx_high(self):
        self.assertRaises(AssertionError, startrek_actions.NavigateToQuadrantAction,
                          qx=8, qy=2, expiry_time=3, priority=10)

    def test_init_qy_low(self):
        self.assertRaises(AssertionError, startrek_actions.NavigateToQuadrantAction,
                          qx=7, qy=-1, expiry_time=3, priority=10)

    def test_init_qy_high(self):
        self.assertRaises(AssertionError, startrek_actions.NavigateToQuadrantAction,
                          qx=7, qy=8, expiry_time=3, priority=10)

    def test_execute_complete(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()
        act=startrek_actions.NavigateToQuadrantAction(qx=7, qy=7)
        act.execute()
        exp_val = (7,7)
        act_val = (gm.quadrant_x, gm.quadrant_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_not_complete(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()
        # Given the seed above, this qx and qy should run Enterprise into a star in it's current quadrant,
        # causeing the action to not be complete.
        act=startrek_actions.NavigateToQuadrantAction(qx=2, qy=6)
        act.execute()
        exp_val = (2,7) # The x and y values for the current quarant, since Enterprise should have run into a star.
        act_val = (gm.quadrant_x, gm.quadrant_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertFalse(act.isComplete())


if __name__ == '__main__':
    unittest.main()
