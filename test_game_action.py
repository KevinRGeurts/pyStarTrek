# standard imports
import unittest

# local imports
from game_action import GameAction, GameActionCombination, GameActionSequence
from dummy_actions import dummyAction

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


class Test_GameActionCombination(unittest.TestCase):
    def test_canInterrupt_no(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        self.assertFalse(combo.canInterrupt())

    def test_canInterrupt_yes(self):
        act1=dummyAction()
        act2=dummyAction()
        act2._canInterrupt=True
        combo = GameActionCombination([act1, act2])
        self.assertTrue(combo.canInterrupt())

    def test_canDoBoth_no(self):
        act1=dummyAction()
        act1._canDoBoth=True
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        other_act=dummyAction()
        self.assertFalse(combo.canDoBoth(other_act))

    def test_canDoBoth_yes(self):
        act1=dummyAction()
        act1._canDoBoth=True
        act2=dummyAction()
        act2._canDoBoth=True
        combo = GameActionCombination([act1, act2])
        other_act=dummyAction()
        self.assertTrue(combo.canDoBoth(other_act))

    def test_canDoBoth_invalid_other_action(self):
        combo = GameActionCombination()
        other_act = float(1.0)  # Invalid type
        self.assertRaises(AssertionError,combo.canDoBoth,other_act)

    def test_isComplete_no(self):
        act1=dummyAction()
        act1._completed=True
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        self.assertFalse(combo.isComplete())

    def test_isComplete_yes(self):
        act1=dummyAction()
        act1._completed=True
        act2=dummyAction()
        act2._completed=True
        combo = GameActionCombination([act1, act2])
        self.assertTrue(combo.isComplete())

    def test_execute(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        # Make sure that prior to execution, the action combination is not complete
        self.assertFalse(combo.isComplete())
        combo.execute()
        # After execution, the action combination should be complete
        self.assertTrue(combo.isComplete())


class Test_GameActionSequence(unittest.TestCase):
    def test_canInterrupt_no(self):
        act1=dummyAction()
        act1._canInterrupt=True
        act2=dummyAction()
        act3=dummyAction()
        act3._canInterrupt=True
        seq = GameActionSequence([act1, act2, act3])
        # Advance the sequence to the 2nd action
        seq.execute()
        self.assertFalse(seq.canInterrupt())

    def test_canInterrupt_yes(self):
        act1=dummyAction()
        act1._canInterrupt=False
        act2=dummyAction()
        act2._canInterrupt=True
        act3=dummyAction()
        act3._canInterrupt=False
        seq = GameActionSequence([act1, act2, act3])
        # Advance the sequence to the 2nd action
        seq.execute()
        self.assertTrue(seq.canInterrupt())

    def test_canDoBoth_no(self):
        act1=dummyAction()
        act1._canDoBoth=False
        act2=dummyAction()
        act2._canDoBoth=True
        act3=dummyAction()
        act3._canDoBoth=False
        seq = GameActionSequence([act1, act2, act3])
        # Advance the sequence to the 2nd action
        seq.execute()
        other_act=dummyAction()
        self.assertFalse(seq.canDoBoth(other_act))

    def test_canDoBoth_yes(self):
        act1=dummyAction()
        act1._canDoBoth=False
        act2=dummyAction()
        act2._canDoBoth=True
        act3=dummyAction()
        act3._canDoBoth=True
        seq = GameActionSequence([act1, act2, act3])
        # Advance the sequence to the 2nd action
        seq.execute()
        other_act=dummyAction()
        self.assertTrue(seq.canDoBoth(other_act))

    def test_canDoBoth_invalid_other_action(self):
        seq = GameActionSequence()
        other_act = float(1.0)  # Invalid type
        self.assertRaises(AssertionError,seq.canDoBoth,other_act)

    def test_isComplete_no(self):
        act1=dummyAction()
        act2=dummyAction()
        seq = GameActionSequence([act1, act2])
        # Executing the sequence should exeucte and complete the first action, but not the second
        seq.execute()
        self.assertFalse(seq.isComplete())

    def test_isComplete_yes_and_execute(self):
        act1=dummyAction()
        act2=dummyAction()
        seq = GameActionSequence([act1, act2])
        # Executing the sequence twice should exeucte and complete both actions
        seq.execute()
        seq.execute()
        self.assertTrue(seq.isComplete())


if __name__ == '__main__':
    unittest.main()
