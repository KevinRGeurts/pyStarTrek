# standard imports
from quopri import decodestring
import unittest
import random
from io import StringIO
from unittest.mock import patch

# local imports
from world_interface import WorldInterface
from pyGameAIFoundation.game_goal import GoalInsistence
from startrek_goals import SurviveGoal, FindKlingonShipGoal, DestroyKlingonShipGoal, ExploreGalaxyGoal
from startrek_goals import RepairResuplyEnterpriseGoal
from startrek_actions import RaiseShieldsAction
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.


class Test_DestroyKlingonShipGoal(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()

    def test_init(self):
        goal=DestroyKlingonShipGoal()
        self.assertEqual(goal.name, "DestroyKlingonShip")

    def test_str(self):
        goal=DestroyKlingonShipGoal()
        exp_val = "Goal: DestroyKlingonShip"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_no_klingon_ship_in_quadrant(self):
        goal=DestroyKlingonShipGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon ship.
    @patch('sys.stdin', StringIO('nav\n6\n1\n'))
    def test_getInsistence_klingon_ship_in_quadrant(self):
        startrek.command_prompt()
        goal=DestroyKlingonShipGoal()
        exp_val=GoalInsistence.HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)


class Test_FindKlingonShipGoal(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()

    def test_init(self):
        goal=FindKlingonShipGoal()
        self.assertEqual(goal.name, "FindKlingonShip")

    def test_str(self):
        goal=FindKlingonShipGoal()
        exp_val = "Goal: FindKlingonShip"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_no_klingon_ship_in_quadrant(self):
        goal=FindKlingonShipGoal()
        exp_val=GoalInsistence.HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon ship.
    @patch('sys.stdin', StringIO('nav\n6\n1\n'))
    def test_getInsistence_klingon_ship_in_quadrant(self):
        startrek.generate_sector()
        startrek.command_prompt()
        goal=FindKlingonShipGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)


class Test_SurviveGoal(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()

    def test_init(self):
        goal=SurviveGoal()
        self.assertEqual(goal.name, "Survive")

    def test_str(self):
        goal=SurviveGoal()
        exp_val = "Goal: Survive"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_no_klingon_ship(self):
        goal=SurviveGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a starbase.
    @patch('sys.stdin', StringIO('nav\n6\n1\n'))
    def test_getInsistence_klingon_ship_shields_down(self):
        startrek.generate_sector()
        startrek.command_prompt()
        goal=SurviveGoal()
        exp_val=GoalInsistence.URGENT
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon ship.
    @patch('sys.stdin', StringIO('nav\n6\n1\n'))
    def test_getInsistence_klingon_ship_shields_up(self):
        # Raise shields
        act=RaiseShieldsAction(shield_energy=500, expiry_time=3, priority=10)
        act.execute()
        # Navigate to a quadrant with a klingon ship
        startrek.generate_sector()
        startrek.command_prompt()
        # Check the insistence of the Survive goal
        goal=SurviveGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)


class Test_ExploreGalaxyGoal(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()
        startrek.generate_sector()

    def test_init(self):
        goal=ExploreGalaxyGoal()
        self.assertEqual(goal.name, "ExploreGalaxy")

    def test_str(self):
        goal=ExploreGalaxyGoal()
        exp_val = "Goal: ExploreGalaxy"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_no_klingon_ship_in_quadrant(self):
        goal=ExploreGalaxyGoal()
        exp_val=GoalInsistence.MEDIUM
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)


class Test_RepairResuplyEnterpriseGoal(unittest.TestCase):
    def setUp(self):
        random.seed(1234567890)
        startrek.initialize_game()

    def test_init(self):
        goal=RepairResuplyEnterpriseGoal()
        self.assertEqual(goal.name, "RepairResuplyEnterprise")

    def test_str(self):
        goal=RepairResuplyEnterpriseGoal()
        exp_val = "Goal: RepairResuplyEnterprise"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_nominal(self):
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_low_energy(self):
        glob_vars.the_game.energy = 499  # Set energy below threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.VERY_HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_low_torpedos(self):
        glob_vars.the_game.photon_torpedoes = 0  # Set number of torpedoes below threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.VERY_HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)
                         
    def test_getInsistence_phaser_damage(self):
        glob_vars.the_game.phaser_damage = 1  # Set phaser damage above threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_photon_damage(self):
        glob_vars.the_game.photon_damage = 1  # Set photon torpedo damage above threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.ZERO
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_weapons_damage(self):
        glob_vars.the_game.phaser_damage = 1  # Set phaser damage above threshold
        glob_vars.the_game.photon_damage = 1  # Set photon torpedo damage above threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.VERY_HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)

    def test_getInsistence_shield_damage(self):
        glob_vars.the_game.shield_control_damage = 1  # Set shield control damage above threshold
        goal=RepairResuplyEnterpriseGoal()
        exp_val=GoalInsistence.VERY_HIGH
        act_val=goal.getInsistence()
        self.assertEqual(act_val, exp_val)


if __name__ == '__main__':
    unittest.main()
