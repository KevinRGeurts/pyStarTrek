# standard imports
from importlib.resources import read_binary
import unittest

# local imports
from game_action import GameAction, GameActionCombination, GameActionSequence
from game_goal import GameGoal, GoalInsistence
from dummy_actions import dummyAction, dummyAction1ofSequence, dummyAction2ofSequence

class Test_GameAction(unittest.TestCase):
    def test_init_read_blackboard_fail(self):
        reader = float(1.0)  # Invalid type
        self.assertRaises(AssertionError, GameAction, read_blackboard=reader)

    def test_init_write_blackboard_fail(self):
        writer = float(1.0)  # Invalid type
        self.assertRaises(AssertionError, GameAction, write_blackboard=writer)
    
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

    def test_getGoalChange_fail(self):
        act = GameAction()
        goal=float(1.0)  # Invalid type
        self.assertRaises(AssertionError, act.getGoalChange, goal)

    def test_getGoalChange(self):
        act = GameAction()
        goal = GameGoal("Test Goal")
        exp_val=GoalInsistence.ZERO
        act_val=act.getGoalChange(goal)
        self.assertEqual(act_val, exp_val)


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

    def test_getGoalChange_fail(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        goal=float(1.0)  # Invalid type
        self.assertRaises(AssertionError, combo.getGoalChange, goal)

    def test_getGoalChange(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionCombination([act1, act2])
        goal = GameGoal("Test Goal")
        exp_val= -(act1.getGoalChange(goal) + act2.getGoalChange(goal))
        act_val=combo.getGoalChange(goal)
        self.assertEqual(act_val, exp_val)


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

    def test_getGoalChange_fail(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionSequence([act1, act2])
        goal=float(1.0)  # Invalid type
        self.assertRaises(AssertionError, combo.getGoalChange, goal)

    def test_getGoalChange(self):
        act1=dummyAction()
        act2=dummyAction()
        combo = GameActionSequence([act1, act2])
        goal = GameGoal("Test Goal")
        exp_val= -(act1.getGoalChange(goal) + act2.getGoalChange(goal))
        act_val=combo.getGoalChange(goal)
        self.assertEqual(act_val, exp_val)

    def test_addAction(self):
        act1=dummyAction()
        act2=dummyAction()
        seq = GameActionSequence([act1])
        seq.addAction(act2)
        self.assertIn(act2, seq._action_list)
        self.assertEqual(len(seq._action_list), 2)

    def test_addAction_fail(self):
        act2=float(1.0) # Invalid type
        seq = GameActionSequence()
        self.assertRaises(AssertionError, seq.addAction, act2)

    def test_blackboard_read_write(self):
        seq = GameActionSequence()
        exp_val = 'test_value'
        seq.writeToBlackBoard('test_key', exp_val)
        act_val = seq.readFromBlackBoard('test_key')
        self.assertEqual(act_val, exp_val)

    def test_sequence_with_blackboard_useage(self):
        seq = GameActionSequence()
        act1 = dummyAction1ofSequence(read_blackboard=seq.readFromBlackBoard,
                                      write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act1)
        act2 = dummyAction2ofSequence(read_blackboard=seq.readFromBlackBoard,
                                      write_blackboard=seq.writeToBlackBoard)
        seq.addAction(act2)
        seq.execute()
        seq.execute()
        exp_val='dummy_data1+dummy_data2'
        act_val = seq.readFromBlackBoard('dummy_action_2ofsequence')
        self.assertEqual(act_val, exp_val)
 

if __name__ == '__main__':
    unittest.main()
