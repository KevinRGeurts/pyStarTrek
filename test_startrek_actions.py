# standard imports
from gettext import find
from typing import Sequence
import unittest
import random

# local imports
from game_action import GameActionSequence
from game_goal import GoalInsistence, GameGoal
from world_interface import WorldInterface
from startrek_goals import DestroyKlingonShipGoal, SurviveGoal, FindKlingonShipGoal
import startrek_actions  # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class LaunchPhotonTorpedoAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()
    
    def test_execute_no_klingon_ship(self):
        act = startrek_actions.LaunchPhotonTorpedoAction(expiry_time=3, priority=10)
        act.execute()
        self.assertFalse(act.isComplete())

    def test_execute_no_torpedos(self):
        glob_vars.the_game.photon_torpedoes = 0
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        # Attempt torpedo launch
        launch = startrek_actions.LaunchPhotonTorpedoAction(expiry_time=3, priority=10)
        launch.execute()
        self.assertFalse(launch.isComplete())

    def test_execute_torpedo_control_damaged(self):
        glob_vars.the_game.photon_damage = 5
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        # Attempt torpedo launch
        launch = startrek_actions.LaunchPhotonTorpedoAction(expiry_time=3, priority=10)
        launch.execute()
        self.assertFalse(launch.isComplete())

    def test_execute(self):
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        launch = startrek_actions.LaunchPhotonTorpedoAction(expiry_time=3, priority=10)
        launch.execute()
        self.assertTrue(launch.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.LaunchPhotonTorpedoAction()
        goal = DestroyKlingonShipGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.LaunchPhotonTorpedoAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


class Test_FindKlingonShipAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()

    def test_execute(self):
        seq=startrek_actions.FindKlingonShipAction(expiry_time=3, priority=10)
        seq.execute() # Execute long range scan to find the klingon ship quadrant.
        seq.execute() # Execute the action to navigate to the klingon ship quadrant.
        # Have we arrived at quadrant (1,6) where the klingon ship is located?
        exp_val = (1, 6)
        act_val = (self._world.quadrant_x, self._world.quadrant_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertTrue(seq.isComplete())

class Test_LongRangeScanAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        self._world = WorldInterface()

    def test_execute(self):
        seq = GameActionSequence()
        act = startrek_actions.LongRangeScanAction(expiry_time=3, priority=10,
                                                   read_blackboard=seq.readFromBlackBoard,
                                                   write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Did we get the expected klingon ship quadrant?
        exp_val = (1,6)
        act_val = (seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.KLINGON_QUAD_X),
                   seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.KLINGON_QUAD_Y))
        self.assertTupleEqual(exp_val, act_val)
        # Did we get the expected starbase quadrant?
        exp_val = (1,7)
        act_val = (seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_QUAD_X),
                   seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_QUAD_Y))
        self.assertTupleEqual(exp_val, act_val)

    def test_execute_long_range_scan_damaged(self):
        glob_vars.the_game.long_range_scan_damage = 1  # Set the long range scan to be damaged.
        seq = GameActionSequence()
        act = startrek_actions.LongRangeScanAction(expiry_time=3, priority=10,
                                                   read_blackboard=seq.readFromBlackBoard,
                                                   write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Should not find any klingon ship quadrant of starbbase quandrant info on blackboard
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.KLINGON_QUAD_X))
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_QUAD_Y))

    def test_isComplete_True(self):
        seq = GameActionSequence()
        act = startrek_actions.LongRangeScanAction(expiry_time=3, priority=10,
                                                   read_blackboard=seq.readFromBlackBoard,
                                                   write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        self.assertTrue(act.isComplete())

    def test_isComplete_False(self):
        act = startrek_actions.LongRangeScanAction()
        self.assertFalse(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.LongRangeScanAction()
        goal = FindKlingonShipGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.LongRangeScanAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


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
