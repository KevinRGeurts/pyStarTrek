# standard imports
from gettext import find
import unittest
import random

# local imports
from game_goal import GoalInsistence, GameGoal
from world_interface import WorldInterface
from star_trek_goals import SurviveGoal, FindKlingonShipGoal
import startrek_actions  # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class Test_RaiseShieldsAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        self._world=WorldInterface()

    def test_init(self):
        act=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        exp_val = (500, 3, 10)
        act_val = (act._shield_energy, act.expiry_time, act.priority)
        self.assertTupleEqual(exp_val, act_val)

    def test_init_negative(self):
        self.assertRaises(AssertionError, startrek_actions.RaiseShieldsAction,
                          shield_energy=-500, expiry_time=3, priority=10)

    def test_execute_raise_complete(self):
        act=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act.execute()
        exp_val=500
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_lower_complete(self):
        # First, get the shields up to 500
        act1=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act1.execute()
        # Now lower the shields to 300
        act2=startrek_actions.RaiseShieldsAction(shield_energy=300, expiry_time=3, priority=10)
        act2.execute()
        exp_val=300
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertTrue(act2.isComplete())

    def test_execute_lower_to_zero_complete(self):
        # First, get the shields up to 500
        act1=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act1.execute()
        # Now lower the shields to 0
        act2=startrek_actions.RaiseShieldsAction(shield_energy=0, expiry_time=3, priority=10)
        act2.execute()
        exp_val=0
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertTrue(act2.isComplete())

    def test_execute_no_change_complete(self):
        # First, get the shields up to 500
        act1=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act1.execute()
        # Now ask again for the shields to be at 500
        act2=startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act2.execute()
        exp_val=500
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertTrue(act2.isComplete())

    def test_execute_raise_incomplete(self):
        act=startrek_actions.RaiseShieldsAction(shield_energy=5000, expiry_time=3, priority=10)
        act.execute()
        exp_val=0
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertFalse(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.RaiseShieldsAction()
        goal = SurviveGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.RaiseShieldsAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


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

    def test_getGoalChange(self):
        act = startrek_actions.NavigateToQuadrantAction()
        goal = FindKlingonShipGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.NavigateToQuadrantAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
