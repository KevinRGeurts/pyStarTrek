# standard imports
import unittest

# local imports
from game_action import GameAction

class Test_GameAction(unittest.TestCase):
    def test_expiry_time_get(self):
        act = GameAction(expiry_time=10)
        exp_val=10
        act_val=act.expiry_time
        self.assertEqual(act_val, exp_val)

    def test_priority_get(self):
        act = GameAction(priority=10)
        exp_val=10
        act_val=act.priority
        self.assertEqual(act_val, exp_val)
    
    def test_canInterrupt(self):
        act = GameAction()
        exp_val=False
        act_val=act.canInterrupt()
        self.assertEqual(act_val, exp_val)

    def test_canDoBoth(self):
        act = GameAction()
        other_act = GameAction()
        exp_val=False
        act_val=act.canDoBoth(other_act)
        self.assertEqual(act_val, exp_val)

    def test_canDoBoth_invalid_other_action(self):
        act = GameAction()
        other_act = float(1.0)  # Invalid type
        self.assertRaises(AssertionError,act.canDoBoth,other_act)

    def test_isComplete(self):
        act = GameAction()
        exp_val=False
        act_val=act.isComplete()
        self.assertEqual(act_val, exp_val)

    def test_execute(self):
        act = GameAction()
        self.assertRaises(NotImplementedError, act.execute)


if __name__ == '__main__':
    unittest.main()
