# standard imports
from gettext import find
from typing import Sequence
import unittest
import random

# local imports
from game_action import GameActionSequence
from game_goal import GoalInsistence, GameGoal
from world_interface import WorldInterface
from startrek_goals import DestroyKlingonShipGoal, SurviveGoal, FindKlingonShipGoal, ExploreGalaxyGoal
from startrek_goals import RepairResuplyEnterpriseGoal, ABSOLUTE_MINIMUM_SHIP_ENERGY
from exceptions import ActionCannotAchieveGoalError
import startrek_actions  # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class Test_FindStarbaseAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()

    def test_execute(self):
        seq=startrek_actions.FindStarbaseAction(expiry_time=3, priority=10)
        while not seq.isComplete(): 
            seq.execute()
        # Have we docked with a starbase??
        self.assertTrue(self._world.docked)


class Test_FirePhasersAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()
    
    def test_execute_no_klingon_ship(self):
        act = startrek_actions.FirePhasersAction(phaser_energy=100, expiry_time=3, priority=10)
        act.execute()
        self.assertFalse(act.isComplete())

    def test_execute_phaser_control_damaged(self):
        glob_vars.the_game.phaser_damage = 5
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        # Attempt to fire phasers
        fire = startrek_actions.FirePhasersAction(phaser_energy=100, expiry_time=3, priority=10)
        fire.execute()
        self.assertFalse(fire.isComplete())

    def test_execute_fire_once(self):
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        fire = startrek_actions.FirePhasersAction(phaser_energy=1000, expiry_time=3, priority=10)
        fire.execute()
        self.assertTrue(fire.isComplete())

    def test_execute_fire_multiple(self):
        shield_action = startrek_actions.RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        while not shield_action.isComplete(): 
            shield_action.execute()
        # Navigate to quadrant with klingon ship
        nav_action = startrek_actions.FindKlingonShipAction()
        while not nav_action.isComplete(): 
            nav_action.execute()
        # Fire phasers multiple times at the klingon ship.
        seq = GameActionSequence(expiry_time=3, priority=10)
        seq.writeToBlackBoard(startrek_actions.BlackboardDatumType.FIRE_PHASERS, True)
        fire_action = startrek_actions.FirePhasersAction(phaser_energy=100, expiry_time=3, priority=10,
                                                         read_blackboard=seq.readFromBlackBoard,
                                                         write_blackboard=seq.writeToBlackBoard)
        seq.addAction(fire_action)
        while not seq.isComplete(): 
            seq.execute()
        self.assertTrue(seq.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.FirePhasersAction()
        goal = DestroyKlingonShipGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.FirePhasersAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


class Test_LaunchPhotonTorpedoAction(unittest.TestCase):
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


class Test_AttackKlingonShipAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()

    def test_execute_torpedo(self):
        # First, we need to find and navigate to a quadrant with a klingon ship.
        seq=startrek_actions.FindKlingonShipAction(expiry_time=3, priority=10)
        while not seq.isComplete(): 
            seq.execute()
        # Have we arrived at a quadrant with a klingon ship?
        self.assertTrue(len(self._world.klingon_ships) > 0)
        # Now we can attack the klingon ship. Should result in torpedo launch.
        num_torp = self._world.photon_torpedoes
        seq = startrek_actions.AttackKlingonShipAction(expiry_time=3, priority=10)
        while not seq.isComplete():
            seq.execute()
        # Is the klingon ship destroyed?
        self.assertTrue(len(self._world.klingon_ships) == 0)
        # Was a photon torpedo launched?
        self.assertTrue(self._world.photon_torpedoes == num_torp - 1)

    def test_execute_phasers(self):
        glob_vars.the_game.photon_torpedoes = 0  # Set photon torpedoes to 0.
        # First, we need to find and navigate to a quadrant with a klingon ship.
        seq=startrek_actions.FindKlingonShipAction(expiry_time=3, priority=10)
        while not seq.isComplete(): 
            seq.execute()
        # Have we arrived at a quadrant with a klingon ship?
        self.assertTrue(len(self._world.klingon_ships) > 0)
        # Now we can attack the klingon ship. Should result in phaser fire (2 times)
        ship_energy_before = self._world.energy
        seq = startrek_actions.AttackKlingonShipAction(expiry_time=3, priority=10)
        while not seq.isComplete():
            seq.execute()
        # Is the klingon ship destroyed?
        self.assertTrue(len(self._world.klingon_ships) == 0)
        # Is ship's energy reduced by amount of phaser energy used?
        self.assertTrue((ship_energy_before - self._world.energy) == 1000)


class Test_FindKlingonShipAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()

    def test_execute(self):
        seq=startrek_actions.FindKlingonShipAction(expiry_time=3, priority=10)
        seq.execute() # Execute long range scan action to find the klingon ship quadrant.
        seq.execute() # Execute the check galactic record action, which should do nothing, since long range scan found klingon.
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


class Test_ShortRangeScanAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        self._world = WorldInterface()

    def test_execute(self):
        # Create and execute an act to get us to a quadrant with a starbase.
        nav_act = startrek_actions.NavigateToQuadrantAction(qx=1, qy=7)
        nav_act.execute()
        exp_val = (1,7)
        act_val = (self._world.quadrant_x, self._world.quadrant_y)
        self.assertTupleEqual(exp_val, act_val)
        # Now create and execute the short range scan action, as part of a sequence, so we have a blackboard.
        seq = GameActionSequence()
        scan_act = startrek_actions.ShortRangeScanAction(expiry_time=3, priority=10,
                                                         read_blackboard=seq.readFromBlackBoard,
                                                         write_blackboard=seq.writeToBlackBoard)
        seq.addAction(scan_act)
        seq.execute()
        # Did we get the expected starbase sector?
        exp_val = (7,6)
        act_val = (seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_SECT_X),
                   seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_SECT_Y))
        self.assertTupleEqual(exp_val, act_val)

    def test_execute_short_range_scan_damaged(self):
        glob_vars.the_game.short_range_scan_damage = 1  # Set the short range scan to be damaged.
        seq = GameActionSequence()
        act = startrek_actions.ShortRangeScanAction(expiry_time=3, priority=10,
                                                    read_blackboard=seq.readFromBlackBoard,
                                                    write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Should not find any starbbase sector info on blackboard
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_SECT_X))

    def test_isComplete_True(self):
        seq = GameActionSequence()
        act = startrek_actions.ShortRangeScanAction(expiry_time=3, priority=10,
                                                    read_blackboard=seq.readFromBlackBoard,
                                                    write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        self.assertTrue(act.isComplete())

    def test_isComplete_False(self):
        act = startrek_actions.ShortRangeScanAction()
        self.assertFalse(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.ShortRangeScanAction()
        goal = RepairResuplyEnterpriseGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.ShortRangeScanAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


class Test_CheckGalacticRecordAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        startrek.long_range_scan()
        self._world = WorldInterface()

    def test_execute(self):
        seq = GameActionSequence()
        act = startrek_actions.CheckGalacticRecordAction(expiry_time=3, priority=10,
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

    def test_execute_computer_controls_damaged(self):
        glob_vars.the_game.computer_damage = 1  # Set the computer controls to be damaged.
        seq = GameActionSequence()
        act = startrek_actions.CheckGalacticRecordAction(expiry_time=3, priority=10,
                                                         read_blackboard=seq.readFromBlackBoard,
                                                         write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Should not find any klingon ship quadrant of starbbase quandrant info on blackboard
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.KLINGON_QUAD_X))
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.BASE_QUAD_Y))

    def test_isComplete_True(self):
        seq = GameActionSequence()
        act = startrek_actions.CheckGalacticRecordAction(expiry_time=3, priority=10,
                                                         read_blackboard=seq.readFromBlackBoard,
                                                         write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        self.assertTrue(act.isComplete())

    def test_isComplete_False(self):
        act = startrek_actions.CheckGalacticRecordAction()
        self.assertFalse(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.CheckGalacticRecordAction()
        goal = FindKlingonShipGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.CheckGalacticRecordAction()
        goal = GameGoal()
        exp_val = GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


class Test_FindUnscannedQuadrantAction(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()
        startrek.long_range_scan()
        self._world = WorldInterface()

    def test_execute(self):
        seq = GameActionSequence()
        act = startrek_actions.FindUnscannedQuadrantAction(expiry_time=3, priority=10,
                                                           read_blackboard=seq.readFromBlackBoard,
                                                           write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Did we get the expected unscanned quadrant?
        exp_val = (0,0)
        act_val = (seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.UNSCANNED_QUAD_X),
                   seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.UNSCANNED_QUAD_Y))
        self.assertTupleEqual(exp_val, act_val)

    def test_execute_computer_controls_damaged(self):
        glob_vars.the_game.computer_damage = 1  # Set the computer controls to be damaged.
        seq = GameActionSequence()
        act = startrek_actions.FindUnscannedQuadrantAction(expiry_time=3, priority=10,
                                                           read_blackboard=seq.readFromBlackBoard,
                                                           write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        # Should not find any klingon ship quadrant of starbbase quandrant info on blackboard
        self.assertIsNone(seq.readFromBlackBoard(startrek_actions.BlackboardDatumType.UNSCANNED_QUAD_X))

    def test_isComplete_True(self):
        seq = GameActionSequence()
        act = startrek_actions.FindUnscannedQuadrantAction(expiry_time=3, priority=10,
                                                           read_blackboard=seq.readFromBlackBoard,
                                                           write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act)
        seq.execute()
        self.assertTrue(act.isComplete())

    def test_isComplete_False(self):
        act = startrek_actions.FindUnscannedQuadrantAction()
        self.assertFalse(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.FindUnscannedQuadrantAction()
        goal = ExploreGalaxyGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.FindUnscannedQuadrantAction()
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

    def test_execute_raise_less_than_asked(self):
        act=startrek_actions.RaiseShieldsAction(shield_energy=5000, expiry_time=3, priority=10)
        act.execute()
        exp_val=2800
        act_val=self._world.shield_level
        self.assertEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_raise_incomplete(self):
        glob_vars.the_game.energy = ABSOLUTE_MINIMUM_SHIP_ENERGY
        act=startrek_actions.RaiseShieldsAction(shield_energy=1, expiry_time=3, priority=10)
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

    def test_execute_with_obstacle(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()
        act=startrek_actions.NavigateToQuadrantAction(qx=2, qy=6)
        act.execute()
        exp_val = (2,6)
        act_val = (gm.quadrant_x, gm.quadrant_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_goal_not_achievable(self):
        seq = GameActionSequence()
        act=startrek_actions.NavigateToQuadrantAction(read_blackboard=seq.readFromBlackBoard,
                                                      write_blackboard=seq.writeToBlackBoard)
        # Since qx and qy are not set, and can't be read from sequence blackbaord, execution will fail,
        # and raise an exception.
        self.assertRaises(ActionCannotAchieveGoalError, act.execute)

    def test_execute_max_attempts_exceeded(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()        
        act=startrek_actions.NavigateToQuadrantAction(qx=2, qy=6, expiry_time=3, priority=10)
        # Since qx and qy, as set, will run Enterprise into a star in it's current quadrant,
        # acton will fail here on the first attempt.
        act.execute()
        self.assertFalse(act.isComplete())
        # Now it will fail on a second attempt.
        act.execute()
        self.assertFalse(act.isComplete())
        # Now on the third attempt, it will fail again, but be marked complete.
        act.execute()
        self.assertTrue(act.isComplete())

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


class Test_DockWithStarbaseAction(unittest.TestCase):
    def test_init(self):
        act=startrek_actions.DockWithStarbaseAction(sx=7, sy=2, expiry_time=3, priority=10)
        exp_val = (7, 2, 3, 10)
        act_val = (act.sx, act.sy, act.expiry_time, act.priority)
        self.assertTupleEqual(exp_val, act_val)

    def test_init_sx_low(self):
        self.assertRaises(AssertionError, startrek_actions.DockWithStarbaseAction,
                          sx=-1, sy=2, expiry_time=3, priority=10)

    def test_init_sx_high(self):
        self.assertRaises(AssertionError, startrek_actions.DockWithStarbaseAction,
                          sx=8, sy=2, expiry_time=3, priority=10)

    def test_init_sy_low(self):
        self.assertRaises(AssertionError, startrek_actions.DockWithStarbaseAction,
                          sx=7, sy=-1, expiry_time=3, priority=10)

    def test_init_sy_high(self):
        self.assertRaises(AssertionError, startrek_actions.DockWithStarbaseAction,
                          sx=7, sy=8, expiry_time=3, priority=10)

    def test_execute_complete(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()
        act=startrek_actions.DockWithStarbaseAction(sx=7, sy=4)
        act.execute()
        exp_val = (7,4)
        act_val = (gm.sector_x, gm.sector_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_with_obstacle(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()
        act=startrek_actions.DockWithStarbaseAction(sx=3, sy=0)
        act.execute()
        exp_val = (3,0)
        act_val = (gm.sector_x, gm.sector_y)
        self.assertTupleEqual(exp_val, act_val)
        self.assertTrue(act.isComplete())

    def test_execute_goal_not_achievable(self):
        seq = GameActionSequence()
        act=startrek_actions.DockWithStarbaseAction(read_blackboard=seq.readFromBlackBoard,
                                                    write_blackboard=seq.writeToBlackBoard)
        # Since sx and sy are not set, and can't be read from sequence blackbaord, execution will fail,
        # and raise an exception.
        self.assertRaises(ActionCannotAchieveGoalError, act.execute)

    def test_execute_max_attempts_exceeded(self):
        random.seed(1234567890)
        gm=glob_vars.the_game        
        startrek.initialize_game()
        startrek.generate_sector()        
        act=startrek_actions.DockWithStarbaseAction(sx=2, sy=6, expiry_time=3, priority=10)
        # Since qx and qy, as set, will run Enterprise into a star in it's current quadrant,
        # acton will fail here on the first attempt.
        act.execute()
        self.assertFalse(act.isComplete())
        # Now it will fail on a second attempt.
        act.execute()
        self.assertFalse(act.isComplete())
        # Now on the third attempt, it will fail again, but be marked complete.
        act.execute()
        self.assertTrue(act.isComplete())

    def test_getGoalChange(self):
        act = startrek_actions.DockWithStarbaseAction()
        goal = RepairResuplyEnterpriseGoal()
        exp_val = -GoalInsistence.HIGH
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)

    def test_getGoalChange_others(self):
        act = startrek_actions.DockWithStarbaseAction()
        goal = GameGoal()
        exp_val = -GoalInsistence.ZERO
        act_val = act.getGoalChange(goal)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
