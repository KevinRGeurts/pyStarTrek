# standard imports
from quopri import decodestring
import unittest
import random
from io import StringIO
from unittest.mock import patch

# local imports
from world_interface import WorldInterface
from game_goal import GoalInsistence
from startrek_goals import SurviveGoal, FindKlingonShipGoal, DestroyKlingonShipGoal
from startrek_actions import RaiseShieldsAction
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.


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


if __name__ == '__main__':
    unittest.main()
