# stanard imports

# local imports
from game_action import GameAction


class ActionManager(object):
    """
    This class manages a list of actions that can be performed in the game.
    """
    def __init__(self):
        """
        Initialize the ActionManager with an empty list of actions.
        """
        # List to store pending actions
        self._action_list = []
        # List of currently executing actions
        self._active = []
        # The current time, a simple counter
        self._currentTime = 0

    @property
    def currentTime(self):
        """
        Return the current time.
        :return: The current time, as int.
        """
        return self._currentTime

    def __len__(self):
        """
        Return the number of pending plus active actions.
        :return: The number of pending plus active actions, as int.
        """
        return len(self._action_list) + len(self._active)

    def scheduleAction(self, action=None):
        """
        Add an action to be executed to the list.
        :param action: The action to be scheduled, as GameAction object.
        :return: None
        """
        assert(isinstance(action, GameAction))
        # Add the action to the list of pending actions, and sort it in descending order of priority.
        self._action_list.append(action)
        self._action_list.sort(key=lambda x: x.priority, reverse=True)
        return None

    def getHighestPriorityActive(self):
        """
        Return the priority level of the highest priority action in the active list.
        :return: The priority level of the highest priority action in the active list, as int.
        Note: Returns 0 if there are no active actions.
        """
        if len(self._active)==0:
            return 0
        else:
            # Sort now,just to make sure.
            self._active.sort(key=lambda x: x.priority, reverse=True)
            # Note: We are assuming that the active list is sorted in descending order of priority.
            return self._active[0].priority
    
    def execute(self):
        """
        Process the ActionManager.
        :return: None
        """

        # Update the time
        self._currentTime+=1

        # Go through the queue to find interrupters
        for action in list(self._action_list):

            # If we drop below the active priority, give up
            if action.priority <= self.getHighestPriorityActive():
                break

            # If we have an interrupter, then interrupt
            if action.canInterrupt():
                # Empty the active list
                self._active.clear()
                # Add the action to the active list, and sort the active list, to maintain priority order
                self._active.append(action)
                self._active.sort(key=lambda x: x.priority, reverse=True)
                # Remove the activeated action from the action list
                self._action_list.remove(action)

        # Try to add as many actions as possible to the active list
        for pending in list(self._action_list):
                
            # Check if the action has timed out
            if pending.expiry_time < self._currentTime:
                # Remove it from the pending action list   
                self._action_list.remove(pending)
                # Move on to the next pending action
                continue
                    
            # If there are no currently active actions, then we can add the pending action to the active list
            if len(self._active) == 0:
                # First, remove the pending action from the action list
                self._action_list.remove(pending)
                # Add it to the active list
                self._active.append(pending)
                # Sort the active list to maintain priority order
                self._active.sort(key=lambda x: x.priority, reverse=True)
            else:
            # There are currently active actions, so check if we can combine the pending action with all active actions
                canCombine=True
                for activeAction in self._active:
                    if not pending.canDoBoth(activeAction):
                        canCombine=False
                        break
                if canCombine:
                    # If we can combine, remove pending action from the action list and add it to the active list
                    self._action_list.remove(pending)
                    self._active.append(pending)
                    # Sort the active list to maintain priority order
                    self._active.sort(key=lambda x: x.priority, reverse=True)
 
        # Process the active list
        for action in list(self._active):
            
            if action.isComplete():
                # Remove completed actions
                self._active.remove(action)
            else:
                # Execute others
                action.execute()

        return None






