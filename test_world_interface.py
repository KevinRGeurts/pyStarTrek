# standard imports
import random
import unittest
from io import StringIO
from unittest.mock import patch

# local imports
from world_interface import WorldInterface
import startrek # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.

class Test_world_interface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        random.seed(1234567890)
        startrek.initialize_game()
        cls._world=WorldInterface()

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a starbase.
    @patch('sys.stdin', StringIO('nav\n6\n1\n'))
    def test_properties(self):
        startrek.generate_sector()
        startrek.command_prompt()
        exp_val=(2267,40,2992,18,2,1,7,5,7,0,0,0,0,0,0,0,0,10,False,False,7,6,64,64,1)
        act_val=(self._world.star_date,
                 self._world.time_remaining,
                 self._world.energy,
                 self._world.klingons,
                 self._world.starbases,
                 self._world.quadrant_x,
                 self._world.quadrant_y,
                 self._world.sector_x,
                 self._world.sector_y,
                 self._world.shield_level,
                 self._world.navigation_damage,
                 self._world.short_range_scan_damage,
                 self._world.long_range_scan_damage,
                 self._world.shield_control_damage,
                 self._world.computer_damage,
                 self._world.photon_torpedo_damage,
                 self._world.phaser_damage,
                 self._world.photon_torpedoes,
                 self._world.docked,
                 self._world.destroyed,
                 self._world.starbase_x,
                 self._world.starbase_y,
                 len(self._world.quadrants)*len(self._world.quadrants[0]),
                 len(self._world.sectors)*len(self._world.sectors[0]),
                 len(self._world.klingon_ships),
                )
        self.assertEqual(exp_val, act_val)
        # Test that total number of Klingons in list self._world.quadrants equals self._world.klingons
        act_val=0
        for j in range(0,8):
            for i in range(0,8):
                    act_val+=self._world.quadrants[j][i].klingons
        exp_val = self._world.klingons
        self.assertEqual(exp_val, act_val)
        # Test that total number of Quadrants in list self._world.quadrants with starbase=True == self._world.starbases
        act_val=0
        for j in range(0,8):
            for i in range(0,8):
                if self._world.quadrants[j][i].starbase==True:
                    act_val+=1
        exp_val = self._world.starbases
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
