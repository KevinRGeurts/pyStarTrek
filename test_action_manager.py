# standard imports
import unittest

# local imports
from action_manager import ActionManager
from game_action import GameAction
from dummy_actions import dummyAction


class Test_action_manager(unittest.TestCase):
    def test_schedule_action(self):
        am = ActionManager()
        action = GameAction(priority=1)
        am.scheduleAction(action)
        # Check if there is an action in the action manager's queue
        self.assertTrue(len(am._action_list) > 0)

    def test_schedule_action_not(self):
        am = ActionManager()
        not_action = float(1.0)
        self.assertRaises(AssertionError, am.scheduleAction, not_action)

    def test_get_highest_priority_active_none(self):
        am = ActionManager()
        # Check if the highest priority action is None when there are no active actions
        self.assertFalse(am.getHighestPriorityActive())

    def test_get_highest_priority_active(self):
        am = ActionManager()
        am._active.append(GameAction())
        am._active.append(GameAction(priority=3))
        am._active.append(GameAction(priority=1))
        # Check that the highest priority active is 3
        exp_val = 3
        act_val = am.getHighestPriorityActive()
        self.assertEqual(exp_val, act_val)

    def test_execute_one_action(self):
        am = ActionManager()
        action = dummyAction(expiry_time=2, priority=1)
        am.scheduleAction(action)
        am.execute()
        # Action manager's action list should be emtpy, and it's active list should have one item in it.
        self.assertTrue(len(am._action_list) == 0)
        self.assertTrue(len(am._active) == 1)
        # And the action should have been completed.
        self.assertTrue(action.isComplete())
        # If we execute again, the action should be removed from the active list.
        am.execute()
        self.assertTrue(len(am._active) == 0)

    def test_execute_second_action_too_low_priority(self):
        am = ActionManager()
        action1 = dummyAction(expiry_time=10, priority=2)
        am._active.append(action1)
        action2 = dummyAction(expiry_time=10, priority=1)
        am.scheduleAction(action2)
        # First execution cycle
        am.execute()
        # Action manager's action list should still have action2 in it.
        self.assertTrue(len(am._action_list) == 1)
        # And the aciton manager's active list should still have action1 in it.
        self.assertTrue(len(am._active) == 1)
        # And action1 should have been completed, while action2 should not have been.
        self.assertTrue(action1.isComplete())
        self.assertFalse(action2.isComplete())
        # Second execution cycle
        # If we execute again, then completed action1 should be removed from the active list, while
        # action2 will still be in the action list, and should not be completed.
        am.execute()
        self.assertTrue(len(am._active) == 0)
        self.assertTrue(len(am._action_list) == 1)
        self.assertFalse(action2.isComplete())
        # Third execution cycle
        # If we execute again, then action2 should be in the active list and completed
        am.execute()
        self.assertTrue(len(am._active) == 1)
        self.assertTrue(len(am._action_list) == 0)
        self.assertTrue(action2.isComplete())
        # Fourth execution cycle
        # If we execute again, then action2 should be removed from the active list.
        am.execute()
        self.assertTrue(len(am._active) == 0)

    def test_execute_time_out(self):
        am = ActionManager()
        action = dummyAction(expiry_time=0, priority=1)
        am.scheduleAction(action)
        am.execute()
        # Action manager's action list should be emtpy, and it's active list should be empty
        self.assertTrue(len(am._action_list) == 0)
        self.assertTrue(len(am._active) == 0)
        # And the action should not have been completed.
        self.assertFalse(action.isComplete())

    def test_execute_interrupt(self):
        am = ActionManager()
        action1 = dummyAction(expiry_time=10, priority=1)
        am._active.append(action1)
        action2 = dummyAction(expiry_time=10, priority=2)
        action2._canInterrupt = True
        am.scheduleAction(action2)
        am.execute()
        # Action manager's action list should be emtpy, and it's active list should have aciton2 in it.
        self.assertTrue(len(am._action_list) == 0)
        self.assertTrue(len(am._active) == 1)
        self.assertTrue(action2 in am._active)
        # And action2 should have been completed.
        self.assertTrue(action2.isComplete())

    def test_execute_cant_combine(self):
        am = ActionManager()
        action1 = dummyAction(expiry_time=10, priority=1)
        am.scheduleAction(action1)
        action2 = dummyAction(expiry_time=10, priority=2)
        am.scheduleAction(action2)
        am.execute()
        # Action manager's action list should contain action1, and it's active list should have action2 in it.
        self.assertTrue(len(am._action_list) == 1)
        self.assertTrue(len(am._active) == 1)
        self.assertTrue(action2 in am._active)
        self.assertTrue(action1 in am._action_list)

    def test_execute_can_combine(self):
        am = ActionManager()
        action1 = dummyAction(expiry_time=10, priority=1)
        action1._canDoBoth = True
        am.scheduleAction(action1)
        action2 = dummyAction(expiry_time=10, priority=2)
        am.scheduleAction(action2)
        am.execute()
        # Action manager's action list should be empty, and it's active list should have action2 and action1 in it.
        self.assertTrue(len(am._action_list) == 0)
        self.assertTrue(len(am._active) == 2)
        self.assertTrue(action2 in am._active)
        self.assertTrue(action1 in am._active)

    def test_len_(self):
        am = ActionManager()
        action1 = dummyAction(expiry_time=10, priority=1)
        am.scheduleAction(action1)
        action2 = dummyAction(expiry_time=10, priority=2)
        am.scheduleAction(action2)
        exp_val = 2
        act_val = len(am)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
