# standard imports
from tkinter import COMMAND
import unittest
import random
import sys
from io import StringIO
from unittest.mock import patch

# local imports
from startrek import Quadrant, SectorType, KlingonShip, Game, game, induce_damage, initialize_game, is_sector_region_empty, klingons_attack, repair_damage
from startrek import distance, compute_direction, print_game_status, command_prompt, navigation_calculator
from startrek import input_double, phaser_controls, sector_type, generate_sector, read_sector
from startrek import short_range_scan, is_docking_location, is_sector_region_empty, print_strings, print_mission
from startrek import print_sector_row, print_sector, long_range_scan, run, _torpedo_control_precheck, _torpedo_controls_input
from startrek import _torpedo_control_launch
from strings import computerStrings

# TODO: Consider factoring out some common setup, like initize_game(), generate_sector(), and separate the tests that
# use that setup into a different unittest.TestCase child.

class Test_test_startrek(unittest.TestCase):

    def test_Quadrant_init(self):
        quad = Quadrant()
        exp_val=('', 0, 0, False, False)
        act_val=(quad.name, quad.klingons, quad.stars, quad.starbase, quad.scanned)
        self.assertEqual(exp_val, act_val)

    def test_SectorType_init(self):
        st = SectorType()
        exp_val=(1, 2, 3, 4, 5)
        act_val=(st.empty, st.star, st.klingon, st.enterprise, st.starbase)
        self.assertEqual(exp_val, act_val)

    def test_KlingonShip_init(self):
        ks = KlingonShip()
        exp_val=(0, 0, 0)
        act_val=(ks.sector_x, ks.sector_y, ks.shield_level)
        self.assertEqual(exp_val, act_val)

    def test_Game_init(self):
        gm = Game()
        exp_val=(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,False,False,0,0,64,64,0)
        act_val=(gm.star_date,
                 gm.time_remaining,
                 gm.energy,
                 gm.klingons,
                 gm.starbases,
                 gm.quadrant_x,
                 gm.quadrant_y,
                 gm.sector_x,
                 gm.sector_y,
                 gm.shield_level,
                 gm.navigation_damage,
                 gm.short_range_scan_damage,
                 gm.long_range_scan_damage,
                 gm.shield_control_damage,
                 gm.computer_damage,
                 gm.photon_damage,
                 gm.phaser_damage,
                 gm.photon_torpedoes,
                 gm.docked,
                 gm.destroyed,
                 gm.starbase_x,
                 gm.starbase_y,
                 len(gm.quadrants)*len(gm.quadrants[0]),
                 len(gm.sector)*len(gm.sector[0]),
                 len(gm.klingon_ships),
                )
        self.assertEqual(exp_val, act_val)

    # TODO: Test objects in the lists of quadrants, sectors, klingon ships
    def test_initialize_game(self):
        random.seed(1234567890)
        initialize_game()
        gm=game
        exp_val=(2266,41,3000,18,2,2,7,3,4,0,0,0,0,0,0,0,0,10,False,False,0,0,64,64,0)
        act_val=(gm.star_date,
                 gm.time_remaining,
                 gm.energy,
                 gm.klingons,
                 gm.starbases,
                 gm.quadrant_x,
                 gm.quadrant_y,
                 gm.sector_x,
                 gm.sector_y,
                 gm.shield_level,
                 gm.navigation_damage,
                 gm.short_range_scan_damage,
                 gm.long_range_scan_damage,
                 gm.shield_control_damage,
                 gm.computer_damage,
                 gm.photon_damage,
                 gm.phaser_damage,
                 gm.photon_torpedoes,
                 gm.docked,
                 gm.destroyed,
                 gm.starbase_x,
                 gm.starbase_y,
                 len(gm.quadrants)*len(gm.quadrants[0]),
                 len(gm.sector)*len(gm.sector[0]),
                 len(gm.klingon_ships),
                )
        self.assertEqual(exp_val, act_val)
        # Test that total number of Klingons in list gm.quadrants equals gm.klingons
        act_val=0
        for j in range(0,8):
            for i in range(0,8):
                    act_val+=gm.quadrants[j][i].klingons
        exp_val = gm.klingons
        self.assertEqual(exp_val, act_val)        # Test that total number of Quadrants in list gm.quadrants with starbase=True == gm.starbases
        # Don't understand why this list comprehension doesn't work
        # act_val = len([[q for q in lofq if q.starbase==True] for lofq in gm.quadrants])
        # But do this instead:
        act_val=0
        for j in range(0,8):
            for i in range(0,8):
                if gm.quadrants[j][i].starbase==True:
                    #print(f"Starbase in quadrant: col={j}, row={i}")
                    act_val+=1
        exp_val = gm.starbases
        self.assertEqual(exp_val, act_val)

    def test_print_game_status_destroyed(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        gm.destroyed=True
        exp_val='MISSION FAILED: ENTERPRISE DESTROYED!!!'
        print_game_status()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_game_status_out_of_energy(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        gm.energy=0
        exp_val='MISSION FAILED: ENTERPRISE RAN OUT OF ENERGY.'
        print_game_status()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_game_status_klingons_destroyed(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        gm.klingons=0
        exp_val='MISSION ACCOMPLISHED: ALL KLINGON SHIPS DESTROYED. WELL DONE!!!'
        print_game_status()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)
        
    def test_print_game_status_out_of_time(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        gm.time_remaining=0
        exp_val='MISSION FAILED: ENTERPRISE RAN OUT OF TIME.'
        print_game_status()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in a printing out the list of possible commands.
    @patch('sys.stdin', StringIO('foo\n'))
    def test_command_prompt(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        exp_val='Enter command: '
        exp_val+='--- Commands -----------------\n'
        exp_val+='nav = Navigation\n'
        exp_val+='srs = Short Range Scan\n'
        exp_val+='lrs = Long Range Scan\n'
        exp_val+='pha = Phaser Control\n'
        exp_val+='tor = Photon Torpedo Control\n'
        exp_val+='she = Shield Control\n'
        exp_val+='com = Access Computer\n'
        exp_val+='qui = Quit the game'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then an invalid command to the computer,
    # Resulting in damage to the computer.
    @patch('sys.stdin', StringIO('com\nfoo\n'))
    def test_computer_controls_bad_command(self):
        random.seed(1234567891)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        self.assertTrue(gm.computer_damage==0)
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Invalid computer command.\n'
        exp_val+='The main computer is malfunctioning.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)
        # Now test that damage was induced
        self.assertTrue(gm.computer_damage>0)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a message that the computer is damaged
    @patch('sys.stdin', StringIO('com\n'))
    def test_computer_controls_damaged(self):
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        # Damage the computer
        gm.computer_damage=1
        exp_val='Enter command: '
        exp_val+='The main computer is damaged. Repairs are underway.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by acceptable navigation calculator inputs
    @patch('sys.stdin', StringIO('com\nnav\n6\n5\n'))
    def test_navigation_calculator(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Enter destination quadrant Y (1--8): '
        exp_val+='Direction: 2.00\n'
        exp_val+='Distance:  4.24'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering quadrant that is current enterprise location
    @patch('sys.stdin', StringIO('com\nnav\n3\n8\n'))
    def test_navigation_calculator_current_enterprise_location(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Enter destination quadrant Y (1--8): '
        exp_val+='That is the current location of the Enterprise.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering x quadrant =0 that is invalid
    @patch('sys.stdin', StringIO('com\nnav\n0\n'))
    def test_navigation_calculator_invalid_X_0(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Invalid X coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering x quadrant =9 that is invalid
    @patch('sys.stdin', StringIO('com\nnav\n9\n'))
    def test_navigation_calculator_invalid_X_9(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Invalid X coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering x quadrant ='foo' that is invalid because it isn't a float
    @patch('sys.stdin', StringIO('com\nnav\nfoo\n'))
    def test_navigation_calculator_invalid_X_not_float(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Invalid X coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering y quadrant =0 that is invalid
    @patch('sys.stdin', StringIO('com\nnav\n3\n0\n'))
    def test_navigation_calculator_invalid_Y_0(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Enter destination quadrant Y (1--8): '
        exp_val+='Invalid Y coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering y quadrant =9 that is invalid
    @patch('sys.stdin', StringIO('com\nnav\n3\n9\n'))
    def test_navigation_calculator_invalid_Y_9(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Enter destination quadrant Y (1--8): '
        exp_val+='Invalid Y coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'nav' command to the computer,
    # followed by entering y quadrant ='foo' that is invalid because it isn't a float
    @patch('sys.stdin', StringIO('com\nnav\n3\nfoo\n'))
    def test_navigation_calculator_invalid_Y_not_float(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Enterprise located in quadrant [3,8].\n'
        exp_val+='Enter destination quadrant X (1--8): '
        exp_val+='Enter destination quadrant Y (1--8): '
        exp_val+='Invalid Y coordinate.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'bas' command to the computer,
    # when the current quadrant does not include a starbase
    @patch('sys.stdin', StringIO('com\nbas\n'))
    def test_starbase_calculator_no_starbase(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='There are no starbases in this quadrant.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_klingons_attack_no_klingons_in_sector(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        generate_sector()
        self.assertFalse(klingons_attack())

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a starbase.
    # Then a 'com' command, then a 'bas' command to the computer, when the current quadrant includes a starbase
    @patch('sys.stdin', StringIO('nav\n6\n1\ncom\nbas\n'))
    def test_starbase_calculator(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with starbase
        gm=game
        initialize_game()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Ask the computer for a starbase computation
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Starbase in sector [5,7].\n'
        exp_val+='Direction: 4.00\n'
        exp_val+='Distance:  0.18'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'tor' command to the computer,
    # when the current quadrant does not include any klingons
    @patch('sys.stdin', StringIO('com\ntor\n'))
    def test_torpedo_calculator_no_klingons(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        generate_sector()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='There are no Klingon ships in this quadrant.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'com' command, then a 'tor' command to the computer, when the current quadrant includes a klingon
    @patch('sys.stdin', StringIO('nav\n6\n1\ncom\ntor\n'))
    def test_torpedo_calculator_klingon(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Ask the computer for a photon torpedo computation
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='Direction 3.18: Klingon ship in sector [5,1].'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 'com' command, then a 'sta' command to the computer
    @patch('sys.stdin', StringIO('com\nsta\n'))
    def test_display_status(self):
        self.maxDiff=None
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='               Time Remaining: 41\n'
        exp_val+='      Klingon Ships Remaining: 18\n'
        exp_val+='                    Starbases: 2\n'
        exp_val+='           Warp Engine Damage: 0\n'
        exp_val+='   Short Range Scanner Damage: 0\n'
        exp_val+='    Long Range Scanner Damage: 0\n'
        exp_val+='       Shield Controls Damage: 0\n'
        exp_val+='         Main Computer Damage: 0\n'
        exp_val+='Photon Torpedo Control Damage: 0\n'
        exp_val+='                Phaser Damage: 0'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'lrs' command to scan part of the galactic record,
    # Then a 'com' command, then a 'rec' command to the computer.
    @patch('sys.stdin', StringIO('lrs\ncom\nrec\n'))
    def test_display_galactic_record(self):
        self.maxDiff=None
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # With this command_prompt() call, we will request a long range scan
        command_prompt()
        # Next, we will ask the computer for the galactic record
        exp_val='Enter command: '
        exp_val+='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator\n'
        exp_val+='Enter computer command: '
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 000 | 000 | 000 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 103 | 008 | 006 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------\n'
        exp_val+='| 000 | 112 | 007 | 008 | 000 | 000 | 000 | 000 |\n'
        exp_val+='-------------------------------------------------'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_phaser_controls_damaged(self):
        gm=game
        initialize_game()
        gm.phaser_damage=1
        exp_val=[]
        exp_val.append('Phasers are damaged. Repairs are underway.')
        exp_val.append('')
        # Call for phasers
        act_val=phaser_controls()
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_phaser_controls_no_klingons(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val=[]
        exp_val.append('There are no Klingon ships in this quadrant.')
        exp_val.append('')
        # Call for phasers
        act_val=phaser_controls()
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'pha' command, then request an invalid phaser energy ('foo').
    @patch('sys.stdin', StringIO('nav\n6\n1\npha\nfoo\n'))
    def test_phaser_controls_klingon_invalid_phaser_energy(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--2992): '
        exp_val+='Invalid energy level.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'pha' command, then request a too low phaser energy (0).
    @patch('sys.stdin', StringIO('nav\n6\n1\npha\n0\n'))
    def test_phaser_controls_klingon_too_low_phaser_energy(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--2992): '
        exp_val+='Invalid energy level.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'pha' command, then request a too high phaser energy (5000).
    @patch('sys.stdin', StringIO('nav\n6\n1\npha\n5000\n'))
    def test_phaser_controls_klingon_too_high_phaser_energy(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--2992): '
        exp_val+='Invalid energy level.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'pha' command, then phaser energy level 2000, resulting in klingon destruction.
    @patch('sys.stdin', StringIO('nav\n6\n1\npha\n2000\n'))
    def test_phaser_controls_klingon_destroyed(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--2992): \n'
        exp_val+='Firing phasers...\n'
        exp_val+='Klingon ship destroyed at sector [5,1].'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)
        # Assert some stuff indicating that the destroyed klingon has been removed from the game.
        self.assertTrue(gm.klingons==17)
        self.assertTrue(gm.quadrants[gm.quadrant_y][gm.quadrant_x].klingons==0)
        self.assertTrue(len(gm.klingon_ships)==0)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command to move to a quadrant with a klingon.
    # Then a 'pha' command, then phaser energy level 500, resulting in klingon damaged.
    @patch('sys.stdin', StringIO('nav\n6\n1\npha\n500\n'))
    def test_phaser_controls_klingon_damaged(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        generate_sector()
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--2992): \n'
        exp_val+='Firing phasers...\n'
        exp_val+='Hit ship at sector [5,1]. Klingon shield strength dropped to 306.\n\n'
        exp_val+='Enterprise hit by ship at sector [5,1]. Shields dropped to 0.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nfoo\n'))
    def test_shield_controls_invalid_command(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an invalid ('foo') shield control command
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Invalid command.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\nfoo\n'))
    def test_shield_controls_add_energy_invalid(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then an invalid amount of energy to add ('foo')
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--3000): '
        exp_val+='Invalid amount of energy.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\n5000\n'))
    def test_shield_controls_add_energy_too_high(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then an invalid amount of energy to add (5000) because it is too high
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--3000): '
        exp_val+='Invalid amount of energy.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\n0\n'))
    def test_shield_controls_add_energy_too_low(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then an invalid amount of energy to add (0) because it is too low
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--3000): '
        exp_val+='Invalid amount of energy.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\n500\n'))
    def test_shield_controls_add(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then a valid amount of energy to add (500)
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--3000): '
        exp_val+='Shield strength is now 500. Energy level is now 2500.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\n500\nshe\nsub\n250\n'))
    def test_shield_controls_sub(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then a valid amount of energy to add (500). The a 'she', 'sub' to subtract 250.
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--500): '
        exp_val+='Shield strength is now 250. Energy level is now 2750.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    @patch('sys.stdin', StringIO('she\nadd\n500\nshe\nsub\n600\n'))
    def test_shield_controls_sub_invalid(self):
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'she' command, then an 'add' shield control command,
    # then a valid amount of energy to add (500). The a 'she', 'sub' to subtract an amount that exceeds 500.
        random.seed(1234567890)
        # Start the game and navigate to quadrant with klingon
        gm=game
        initialize_game()
        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--500): '
        exp_val+='Invalid amount of energy.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_klingons_attack_no_klingons_in_sector(self):
        random.seed(1234567890)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Run the test
        gm=game
        initialize_game()
        generate_sector()
        (output,something)=klingons_attack()
        self.assertFalse(something)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in:
    #   (1) Raising shields so enterprise isn't destroyed when hit: she / add / 500
    #   (2) Navigating to quadrant with klingon and starbase: nav / 6 / 1
    #   (3) Navigating a little in the sector to give klingon opportunity to hit Enterprise: nav / 6 / .1
    @patch('sys.stdin', StringIO('she\nadd\n500\nnav\n6\n1\nnav\n6\n.1\n'))
    def test_klingons_attack_Enterprise_hit(self):
        self.maxDiff=None
        random.seed(1234567890)
        # Start the game and navigate to quadrant with starbase
        gm=game
        initialize_game()
        generate_sector()
        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # This command_prompt() will eat the nav/6/1 sequence
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Navigate within sector
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Warp engines engaged.\n'
        exp_val+='X: 1  2  3  4  5  6  7  8\n'
        exp_val+='Y:-=--=--=--=--=--=--=--=-          Region: Wolf 359\n'
        exp_val+='1             +K+                    Quadrant: [2,8]\n'
        exp_val+='2                                      Sector: [5,8]\n'
        exp_val+='3        *                           Stardate: 2267\n'
        exp_val+='4                              Time remaining: 40\n'
        exp_val+='5                                   Condition: RED\n'
        exp_val+='6  *                                   Energy: 2492\n'
        exp_val+='7                      >S<            Shields: 500\n'
        exp_val+='8             <E>            Photon Torpedoes: 10\n'
        exp_val+='  -=--=--=--=--=--=--=--=-             Docked: False\n'
        exp_val+='\n'
        exp_val+='Condition RED: Klingon ship detected.\n'
        exp_val+='\n'
        exp_val+='Enterprise hit by ship at sector [5,1]. Shields dropped to 429.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in:
    #   (1) Raising shields so enterprise isn't destroyed before docking: she / add / 500
    #   (2) Navigating to quadrant with klingon and starbase: nav / 6 / 1
    #   (3) Navigating to dock with the starbaose: nav / 1.59 / 0.28
    #   (4) Sending a torpedo off to nowhere, to give the klingon a chance to fire on docked Enterprise: tor / 3
    @patch('sys.stdin', StringIO('nav\n6\n1\nshe\nadd\n500\nnav\n1.59\n0.28\ntor\n3\n'))
    def test_klingons_attack_docked(self):
        self.maxDiff=None
        random.seed(1234567890)
        # Start the game and navigate to quadrant with starbase
        gm=game
        initialize_game()
        generate_sector()
        # This command_prompt() will eat the nav/6/1 sequence
        command_prompt()
        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # This command_prompt() will eat the nav/1.59/0.28 sequence
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Navigate to dock with starbase
        exp_val='Enter command: '
        exp_val+='Enter firing direction (1.0--9.0, 1=right,3=up,5=left,7=down): \n'
        exp_val+='Photon torpedo fired...\n'
        exp_val+='  [8,6]\n'
        exp_val+='  [8,5]\n'
        exp_val+='  [8,4]\n'
        exp_val+='  [8,3]\n'
        exp_val+='  [8,2]\n'
        exp_val+='  [8,1]\n'
        exp_val+='Photon torpedo failed to hit anything.\n'
        exp_val+='Enterprise hit by ship at sector [5,1]. No damage due to starbase shields.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in:
    #   (1) Navigating to quadrant with klingon and starbase: nav / 6 / 1
    #   (2) Raising shields so enterprise isn't destroyed before docking: she / add / 1000
    #   (3) Photon torpedo the Klingon: tor / 3.18
    #   At this point, artificially induce damage to all systems, to provide ability to test repair on docking.
    #   (4) Navigating to dock with the starbaose
    @patch('sys.stdin', StringIO('nav\n6\n1\nshe\nadd\n500\ntor\n3.18\nnav\n1\n.2\n'))
    def test_docked_for_repair(self):
        self.maxDiff=None
        random.seed(1234567890)
        # Start the game and navigate to quadrant with starbase
        gm=game
        initialize_game()
        generate_sector()
        # This command_prompt() will eat the nav/6/1 sequence
        command_prompt()
        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # This command_prompt() will eat firing the photon torpedo
        command_prompt()
        # Artificially provide some damage
        gm.navigation_damage = 1
        gm.short_range_scan_damage = 1
        gm.long_range_scan_damage = 1
        gm.shield_control_damage = 1
        gm.computer_damage = 1
        gm.photon_damage = 1
        gm.phaser_damage = 1
        gm.shield_level = 1
        # Check for some damage and less than full torpedo load
        self.assertEqual(1,gm.navigation_damage)
        self.assertEqual(9,gm.photon_torpedoes)
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Navigate to dock with starbase
        exp_val='Enter command: '
        exp_val+='Warp engines damaged. Maximum warp factor: 0.8999999999999999\n'
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--0.8999999999999999): '
        exp_val+='Warp engines engaged.\n'
        exp_val+='X: 1  2  3  4  5  6  7  8\n'
        exp_val+='Y:-=--=--=--=--=--=--=--=-          Region: Wolf 359\n'
        exp_val+='1                                    Quadrant: [2,8]\n'
        exp_val+='2                                      Sector: [7,8]\n'
        exp_val+='3        *                           Stardate: 2267\n'
        exp_val+='4                              Time remaining: 40\n'
        exp_val+='5                                   Condition: GREEN\n'
        exp_val+='6  *                                   Energy: 3000\n'
        exp_val+='7                      >S<            Shields: 0\n'
        exp_val+='8                   <E>      Photon Torpedoes: 10\n'
        exp_val+='  -=--=--=--=--=--=--=--=-             Docked: True\n'
        exp_val+='\n'
        exp_val+='Lowering shields as part of docking sequence...\n'
        exp_val+='Enterprise successfully docked with starbase.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)
        # Assert that Enterprise has been repaired and restocked
        self.assertEqual(3000,gm.energy)
        self.assertEqual(10,gm.photon_torpedoes)
        self.assertEqual(0,gm.navigation_damage)
        self.assertEqual(0,gm.short_range_scan_damage)
        self.assertEqual(0,gm.long_range_scan_damage)
        self.assertEqual(0,gm.shield_control_damage)
        self.assertEqual(0,gm.computer_damage)
        self.assertEqual(0,gm.photon_damage)
        self.assertEqual(0,gm.phaser_damage)
        self.assertEqual(0,gm.shield_level)

    def test_is_docking_location(self):
        random.seed(1234567890)
        # Start the game and navigate to quadrant with starbase
        gm=game
        initialize_game()
        generate_sector()

        # This command_prompt() will eat the she/add/500 sequence
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Adjust shields
        exp_val='Enter command: '
        exp_val+='--- Shield Controls ----------------\n'
        exp_val+='add = Add energy to shields.\n'
        exp_val+='sub = Subtract energy from shields.\n'
        exp_val+='Enter shield control command: '
        exp_val+='Enter amount of energy (1--500): '
        exp_val+='Invalid amount of energy.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)
        self.assertTrue(False) # Too make sure this fails, until I resolve the apparent inability to dock

    # TODO: Also check that repair messages are printed
    def test_repair_damage(self):
        gm=game
        gm.navigation_damage=2
        gm.short_range_scan_damage=1
        gm.long_range_scan_damage=1
        gm.shield_control_damage=1
        gm.computer_damage=1
        gm.photon_damage=1
        gm.phaser_damage=1
        # Repair navigation
        repair_damage()
        exp_val=1
        act_val = gm.navigation_damage
        self.assertEqual(exp_val, act_val)
        repair_damage()
        exp_val=0
        act_val = gm.navigation_damage
        self.assertEqual(exp_val, act_val)
        # Repair short range scan
        repair_damage()
        exp_val=0
        act_val = gm.short_range_scan_damage
        self.assertEqual(exp_val, act_val)
        # Repair long range scan
        repair_damage()
        exp_val=0
        act_val = gm.long_range_scan_damage
        self.assertEqual(exp_val, act_val)
        # Repair shield control
        repair_damage()
        exp_val=0
        act_val = gm.shield_control_damage
        self.assertEqual(exp_val, act_val)
        # Repair computer
        repair_damage()
        exp_val=0
        act_val = gm.computer_damage
        self.assertEqual(exp_val, act_val)
        # Repair photon
        repair_damage()
        exp_val=0
        act_val = gm.photon_damage
        self.assertEqual(exp_val, act_val)
        # Repair phaser
        repair_damage()
        exp_val=0
        act_val = gm.phaser_damage
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_random(self):
        initialize_game()
        random.seed(1234567896)
        induce_damage(-1)
        gm=game
        exp_val=(0,0,0,0,4,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_navigation(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(0)
        gm=game
        exp_val=(3,0,0,0,0,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_short_range_scan(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(1)
        gm=game
        exp_val=(0,3,0,0,0,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_long_range_scan(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(2)
        gm=game
        exp_val=(0,0,3,0,0,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_shield_control(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(3)
        gm=game
        exp_val=(0,0,0,3,0,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_computer(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(4)
        gm=game
        exp_val=(0,0,0,0,3,0,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_photon(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(5)
        gm=game
        exp_val=(0,0,0,0,0,3,0)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_induce_damage_phaser(self):
        random.seed(1234567891)
        initialize_game()
        induce_damage(6)
        gm=game
        exp_val=(0,0,0,0,0,0,3)
        act_val=(gm.navigation_damage,
                gm.short_range_scan_damage,
                gm.long_range_scan_damage,
                gm.shield_control_damage,
                gm.computer_damage,
                gm.photon_damage,
                gm.phaser_damage)
        self.assertEqual(exp_val, act_val)

    def test_distance(self):
        exp_val=7.071067812
        act_val=distance(2,3,7,8)
        self.assertAlmostEqual(exp_val, act_val)

    def test_compute_direction(self):
        # x1=x2, y1<y2
        exp_val=7
        act_val=compute_direction(2,5,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1=x2, y1>y2
        exp_val=3
        act_val=compute_direction(2,7,2,5)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1=y2
        exp_val=1
        act_val=compute_direction(2,7,4,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1=y2
        exp_val=5
        act_val=compute_direction(4,7,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1<y2
        exp_val=6
        act_val=compute_direction(4,5,2,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1>x2, y1>y2
        exp_val=4
        act_val=compute_direction(4,7,2,5)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1<y2
        exp_val=8
        act_val=compute_direction(2,5,4,7)
        self.assertAlmostEqual(exp_val, act_val)
        # x1<x2, y1>y2
        exp_val=2
        act_val=compute_direction(2,7,4,5)
        self.assertAlmostEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in valid input of a float
    @patch('sys.stdin', StringIO('7.56\n'))
    def test_input_double(self):
        exp_val=7.56
        act_val=input_double('Enter a valid floating point number:')
        self.assertAlmostEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in invalid input
    @patch('sys.stdin', StringIO('foo\n'))
    def test_input_double_invalid(self):
        act_val=input_double('Enter a valid floating point number:')
        self.assertFalse(act_val)

    def test_read_sector(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        short_range_scan() # Should not really be needed, but helpful for debugging test
        # for j in range(8):
        #     for i in range(8):
        #         print(f"for (x,y)=({i},{j}), sector type = {read_sector(j,i)}")
        # Note: read_sector(yi,xi), both 0-indexed
        self.assertEqual(sector_type.star, read_sector(0,2))
        self.assertEqual(sector_type.enterprise, read_sector(4,3))

    def test_is_docking_location(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Place a starbase at [row=4, 0-indexed][row=5, 0-indexed]=[x=6,y=5]
        gm.sector[4][5]=sector_type.starbase
        self.assertTrue(is_docking_location(3,4))
        self.assertTrue(is_docking_location(3,5))
        self.assertTrue(is_docking_location(3,6))
        self.assertTrue(is_docking_location(4,4))
        self.assertTrue(is_docking_location(4,5))
        self.assertTrue(is_docking_location(4,6))
        self.assertTrue(is_docking_location(5,4))
        self.assertTrue(is_docking_location(5,5))
        self.assertTrue(is_docking_location(5,6))
        self.assertFalse(is_docking_location(2,5))
        self.assertFalse(is_docking_location(6,5))
        self.assertFalse(is_docking_location(4,3))
        self.assertFalse(is_docking_location(4,7))

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a direction (1), then a speed (6) too large for the
    # damaged navigation, i.e., the engines.
    @patch('sys.stdin', StringIO('nav\n1\n6\n'))
    def test_navigation_damaged(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        gm.navigation_damage=1
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Warp engines damaged. Maximum warp factor: 0.8\n'
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--0.8): '
        exp_val+='Invalid warp factor.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then an invalid direction (0.5).
    @patch('sys.stdin', StringIO('nav\n0.5\n'))
    def test_navigation_invalid_course_low(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Invalid course.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then an invalid direction (9.1).
    @patch('sys.stdin', StringIO('nav\n9.1\n'))
    def test_navigation_invalid_course_high(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Invalid course.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then an invalid direction ('foo').
    @patch('sys.stdin', StringIO('nav\nfoo\n'))
    def test_navigation_invalid_course_invalid(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Invalid course.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a valid direction (1), but a too low
    # warp factor (0.05).
    @patch('sys.stdin', StringIO('nav\n1\n0.05\n'))
    def test_navigation_warp_factor_low(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Invalid warp factor.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a valid direction (1), but an invalid
    # warp factor ('foo').
    @patch('sys.stdin', StringIO('nav\n1\nfoo\n'))
    def test_navigation_warp_factor_invalid(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Invalid warp factor.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val) 

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a valid direction (1), and a
    # warp factor that is okay from a damage standpoint, but exceeds remaining energy (6).
    @patch('sys.stdin', StringIO('nav\n1\n6\n'))
    def test_navigation_insufficent_energy(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        # Set energy very low, so it is insufficent for requested warp factor
        gm.energy=40
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Unable to comply. Insufficient energy to travel that speed.'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a valid direction (1), and a
    # warp factor that is okay from a damage standpoint, but exceeds remaining energy (6).
    @patch('sys.stdin', StringIO('nav\n1\n6\n'))
    def test_navigation_successful(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Warp engines engaged.\n'
        exp_val+='X: 1  2  3  4  5  6  7  8\n'
        exp_val+='Y:-=--=--=--=--=--=--=--=-          Region: Tau Alpha C\n'
        exp_val+='1              *                     Quadrant: [8,8]\n'
        exp_val+='2                                      Sector: [8,5]\n'
        exp_val+='3        *                           Stardate: 2267\n'
        exp_val+='4                              Time remaining: 40\n'
        exp_val+='5                      <E>          Condition: GREEN\n'
        exp_val+='6  *                 *                 Energy: 2952\n'
        exp_val+='7                       *             Shields: 0\n'
        exp_val+='8                    *       Photon Torpedoes: 10\n'
        exp_val+='  -=--=--=--=--=--=--=--=-             Docked: False'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'nav' command, then a direction (3), and a
    # warp factor (0.3) that run the Enterprise into a star.
    @patch('sys.stdin', StringIO('nav\n3\n0.3\n'))
    def test_navigation_obstacle(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Attempt navigation with damage
        exp_val='Enter command: '
        exp_val+='Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): '
        exp_val+='Enter warp factor (0.1--8.0): '
        exp_val+='Warp engines engaged.\n'
        exp_val+='Encountered obstacle within quadrant.\n'
        exp_val+='X: 1  2  3  4  5  6  7  8\n'
        exp_val+='Y:-=--=--=--=--=--=--=--=-          Region: Pegos Minor\n'
        exp_val+='1        *                           Quadrant: [3,8]\n'
        exp_val+='2                                      Sector: [4,4]\n'
        exp_val+='3           *                        Stardate: 2266\n'
        exp_val+='4          <E>                 Time remaining: 41\n'
        exp_val+='5                                   Condition: GREEN\n'
        exp_val+='6                 *     *              Energy: 2998\n'
        exp_val+='7     *        *     *                Shields: 0\n'
        exp_val+='8                            Photon Torpedoes: 10\n'
        exp_val+='  -=--=--=--=--=--=--=--=-             Docked: False'
        command_prompt()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

        
    def test_is_sector_region_empty(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        short_range_scan()
        # For debugging:
        # for j in range(0,8):
        #     for i in range(0,8):
        #         print(f"({j},{i})={is_sector_region_empty(j,i)}")
        # Check all the NOT empty regions.
        # This is the sector being tested against. X,Y,X are the three sectors
        # that do not contain a star or the Enterprise, which also return False.
        # A is a sector that will return True, even though lower-left AND lower-right are not empty.
        #
        # -=--=--=--=--=--=--=--=-          Region: Pegos Minor
        #        *                           Quadrant: [3,8]
        #                                      Sector: [4,5]
        #           *                        Stardate: 2266
        #                              Time remaining: 41
        #          <E>       A              Condition: GREEN
        #                 *  X  *              Energy: 3000
        #     *        *  Y  *                Shields: 0
        #                 Z          Photon Torpedoes: 10
        # -=--=--=--=--=--=--=--=-             Docked: False
        self.assertFalse(is_sector_region_empty(0,2))
        self.assertFalse(is_sector_region_empty(2,3))
        self.assertFalse(is_sector_region_empty(4,3))
        self.assertFalse(is_sector_region_empty(5,5))
        self.assertFalse(is_sector_region_empty(5,6))
        self.assertFalse(is_sector_region_empty(5,7))
        self.assertFalse(is_sector_region_empty(6,1))
        self.assertFalse(is_sector_region_empty(6,4))
        self.assertFalse(is_sector_region_empty(6,5))
        self.assertFalse(is_sector_region_empty(6,6))
        self.assertFalse(is_sector_region_empty(7,5))
        # Now check some empty regions.
        self.assertTrue(is_sector_region_empty(4,6))  
    
    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in issuing a 'qui command, which will immediately exit game.
    @patch('sys.stdin', StringIO('qui\n'))
    def test_run(self):
        random.seed(1234567890)
        # Run the game. Shoud raise a SystemExit exception
        # NOTE: This is quite a crude test of runI()
        self.assertRaises(SystemExit, run)

    def test_long_range_scan_damaged(self):
        self.maxDiff=None
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Artificially damager the long range scanners
        gm.long_range_scan_damage=1
        exp_val=['Long range scanner is damaged. Repairs are underway.','']
        act_val = long_range_scan()
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_long_range_scan(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val=[]
        exp_val.append('-------------------')
        exp_val.append('| 103 | 008 | 006 |')
        exp_val.append('-------------------')
        exp_val.append('| 112 | 007 | 008 |')
        exp_val.append('-------------------')
        exp_val.append('| 000 | 000 | 000 |')
        exp_val.append('-------------------')
        exp_val.append('')
        act_val=long_range_scan()
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_generate_sector(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val=[[1, 1, 2, 1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 2, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 1, 1, 4, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1, 2, 1, 2],
                    [1, 2, 1, 1, 2, 1, 2, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]]
        act_val=game.sector
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_short_range_scan(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val=[]
        exp_val.append('X: 1  2  3  4  5  6  7  8')
        exp_val.append('Y:-=--=--=--=--=--=--=--=-          Region: Pegos Minor')
        exp_val.append('1        *                           Quadrant: [3,8]')
        exp_val.append('2                                      Sector: [4,5]')
        exp_val.append('3           *                        Stardate: 2266')
        exp_val.append('4                              Time remaining: 41')
        exp_val.append('5          <E>                      Condition: GREEN')
        exp_val.append('6                 *     *              Energy: 3000')
        exp_val.append('7     *        *     *                Shields: 0')
        exp_val.append('8                            Photon Torpedoes: 10')
        exp_val.append('  -=--=--=--=--=--=--=--=-             Docked: False')
        exp_val.append('')
        act_val=short_range_scan()
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_sector(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val=[]
        exp_val.append('X: 1  2  3  4  5  6  7  8')
        exp_val.append('Y:-=--=--=--=--=--=--=--=-          Region: Pegos Minor')
        exp_val.append('1        *                           Quadrant: [3,8]')
        exp_val.append('2                                      Sector: [4,5]')
        exp_val.append('3           *                        Stardate: 2266')
        exp_val.append('4                              Time remaining: 41')
        exp_val.append('5          <E>                      Condition: GREEN')
        exp_val.append('6                 *     *              Energy: 3000')
        exp_val.append('7     *        *     *                Shields: 0')
        exp_val.append('8                            Photon Torpedoes: 10')
        exp_val.append('  -=--=--=--=--=--=--=--=-             Docked: False')
        act_val=print_sector(gm.quadrants[gm.quadrant_y][gm.quadrant_x])
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_sector_row(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        sb='foo'
        suffix='bar'
        exp_val='foo                *     * bar'
        act_val=print_sector_row(sb,5,suffix)
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_mission(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        exp_val='Mission: Destroy 18 Klingon ships in 41 stardates with 2 starbases.'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Print the string
        print_mission()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_print_strings(self):
        exp_val='--- Main Computer --------------\n'
        exp_val+='rec = Cumulative Galatic Record\n'
        exp_val+='sta = Status Report\n'
        exp_val+='tor = Photon Torpedo Calculator\n'
        exp_val+='bas = Starbase Calculator\n'
        exp_val+='nav = Navigation Calculator'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Print the string
        print_strings(computerStrings)
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)


    def test_torpedo_precheck_damaged(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Artificially damage the torpedo control
        gm.photon_damage=1
        exp_val=[] # list of strings
        exp_val.append('Photon torpedo control is damaged. Repairs are underway.')
        exp_val.append('')
        exp_val=(False,exp_val)
        act_val = _torpedo_control_precheck()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)

    def test_torpedo_precheck_no_torpedos_left(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Artificially use up all torpedoes
        gm.photon_torpedoes=0
        exp_val=[] # list of strings
        exp_val.append('Photon torpedoes exhausted.')
        exp_val.append('')
        exp_val=(False,exp_val)
        act_val = _torpedo_control_precheck()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)

    def test_torpedo_precheck_no_klingons(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        # Note: There are no klingons in this sector, given teh random seed.
        exp_val=[] # list of strings
        exp_val.append('There are no Klingon ships in this quadrant.')
        exp_val.append('')
        exp_val=(False,exp_val)
        act_val = _torpedo_control_precheck()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result issuing 3 invalid torpedo directions ['foo', 9.1, 0.9]
    @patch('sys.stdin', StringIO('foo\n9.1\n0.9\n'))
    def test_torpedo_input_invalid(self):
        # Test completely invalid input ('foo')
        exp_val=(False, ['Invalid direction.', ''], False)
        act_val = _torpedo_controls_input()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)
        
        # Test high invalid input ('9.1')
        exp_val=(False, ['Invalid direction.', ''], 9.1)
        act_val = _torpedo_controls_input()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)

        # Test low invalid input ('0.9')
        exp_val=(False, ['Invalid direction.', ''], 0.9)
        act_val = _torpedo_controls_input()
        # Assert the output matches the expected value
        self.assertTupleEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in raising shields and then navigating to a sector with a klingon.
    @patch('sys.stdin', StringIO('she\nadd\n500\nnav\n5\n1\n'))
    def test_launch_torpedo_hit_star(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        command_prompt() # Raise shields
        command_prompt() # Navigate
        exp_val=[] # list of strings
        exp_val.append('')
        exp_val.append('Photon torpedo fired...')
        exp_val.append('  [4,5]')
        exp_val.append('  [4,4]')
        exp_val.append('  [3,4]')
        exp_val.append('  [3,3]')
        exp_val.append("The torpedo was captured by a star's gravitational field at sector [3,3].")
        exp_val.append("Enterprise hit by ship at sector [5,1]. Shields dropped to 320.")
        exp_val.append('')
        # Launch torpedo that will hit a star
        act_val = _torpedo_control_launch(3.5)
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in raising shields and then navigating to a sector with a klingon and a starbase
    @patch('sys.stdin', StringIO('she\nadd\n500\nnav\n5\n1\n'))
    def test_launch_torpedo_hit_starbase(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        command_prompt() # Raise shields
        command_prompt() # Navigate
        exp_val=[] # list of strings
        exp_val.append('')
        exp_val.append('Photon torpedo fired...')
        exp_val.append('  [4,5]')
        exp_val.append('  [5,5]')
        exp_val.append('  [5,6]')
        exp_val.append('  [6,6]')
        exp_val.append('  [7,6]')
        exp_val.append('  [8,6]')
        exp_val.append('  [8,7]')
        exp_val.append("The Enterprise destroyed a Federation starbase at sector [8,7]!")
        exp_val.append("Enterprise hit by ship at sector [5,1]. Shields dropped to 320.")
        exp_val.append('')
        # Launch torpedo that will hit a starbase
        act_val = _torpedo_control_launch(8.5)
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in raising shields and then navigating to a sector with a klingon and a starbase
    @patch('sys.stdin', StringIO('she\nadd\n500\nnav\n5\n1\n'))
    def test_launch_torpedo_hit_klingon(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        command_prompt() # Raise shields
        command_prompt() # Navigate
        exp_val=[] # list of strings
        exp_val.append('')
        exp_val.append('Photon torpedo fired...')
        exp_val.append('  [4,5]')
        exp_val.append('  [4,4]')
        exp_val.append('  [4,3]')
        exp_val.append('  [5,3]')
        exp_val.append('  [5,2]')
        exp_val.append('  [5,1]')
        exp_val.append("Klingon ship destroyed at sector [5,1].")
        exp_val.append('')
        # Launch torpedo that will hit a klingon
        act_val = _torpedo_control_launch(2.69)
        self.assertEqual(exp_val, act_val)


    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in raising shields and then navigating to a sector with a klingon and a starbase
    @patch('sys.stdin', StringIO('she\nadd\n500\nnav\n5\n1\n'))
    def test_launch_torpedo_hit_nothing(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        command_prompt() # Raise shields
        command_prompt() # Navigate
        exp_val=[] # list of strings
        exp_val.append('')
        exp_val.append('Photon torpedo fired...')
        exp_val.append('  [4,5]')
        exp_val.append('  [4,6]')
        exp_val.append('  [4,7]')
        exp_val.append('  [4,8]')
        exp_val.append("Photon torpedo failed to hit anything.")
        exp_val.append("Enterprise hit by ship at sector [5,1]. Shields dropped to 320.")
        exp_val.append('')
        # Launch torpedo that will hit nothing
        act_val = _torpedo_control_launch(7)
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
