# standard imports
import unittest

# local imports
from game_goal import GameGoal, GoalInsistence


class Test_GameGoal(unittest.TestCase):
    def test_init(self):
        goal=GameGoal("Test Goal")
        self.assertEqual(goal.name, "Test Goal")

    def test_str(self):
        goal=GameGoal("Test Goal")
        exp_val = "Goal: Test Goal"
        act_val = str(goal)
        self.assertEqual(act_val, exp_val)

    def test_getInsistance(self):
        goal=GameGoal("Test Goal")
        self.assertRaises(NotImplementedError, goal.getInsistence)




if __name__ == '__main__':
    unittest.main()
