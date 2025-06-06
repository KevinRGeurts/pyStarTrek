# standard imports
import unittest

# local imports
from gob import Gob
from game_goal import GameGoal
from game_action import GameAction

class Test_gob(unittest.TestCase):
    def test_add_remove_goal(self):
        gob = Gob()
        self.assertEqual(len(gob._goals), 0)
        goal = GameGoal(name="TestGoal")
        gob.add_goal(goal)
        self.assertEqual(len(gob._goals), 1)
        gob.remove_goal(goal)
        self.assertEqual(len(gob._goals), 0)

    def test_remove_missing_goal(self):
        gob = Gob()
        goal1 = GameGoal(name="TestGoal")
        gob.add_goal(goal1)
        goal2 = GameGoal(name="AnotherGoal")
        gob.remove_goal(goal2)
        self.assertEqual(len(gob._goals), 1)

    def test_add_remove_goal_not_goal(self):
        gob = Gob()
        not_goal=GameAction()
        self.assertRaises(AssertionError, gob.add_goal, not_goal)
        self.assertRaises(AssertionError, gob.remove_goal, not_goal)

    def test_add_remove_action(self):
        gob = Gob()
        self.assertEqual(len(gob._actions), 0)
        action = GameAction()
        gob.add_action(action)
        self.assertEqual(len(gob._actions), 1)
        gob.remove_action(action)
        self.assertEqual(len(gob._actions), 0)

    def test_add_remove_action_not_action(self):
        gob = Gob()
        not_action=GameGoal('test goal')
        self.assertRaises(AssertionError, gob.add_action, not_action)
        self.assertRaises(AssertionError, gob.remove_action, not_action)

    def test_remove_missing_action(self):
        gob = Gob()
        act1 = GameAction()
        gob.add_action(act1)
        act2 = GameAction()
        gob.remove_action(act2)
        self.assertEqual(len(gob._actions), 1)



if __name__ == '__main__':
    unittest.main()
