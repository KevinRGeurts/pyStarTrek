# standard imports
import unittest
import random
import sys
from io import StringIO
from unittest.mock import patch

# local imports
from startrek import Quadrant, SectorType, KlingonShip, Game, game, induce_damage, initialize_game, repair_damage
from startrek import distance, compute_direction, print_game_status, command_prompt, navigation_calculator
from startrek import input_double, input_int, phaser_controls, sector_type, generate_sector

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
        exp_val+='Direction 3.48: Klingon ship in sector [4,3].'
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
        exp_val+='| 000 | 113 | 008 | 006 | 000 | 000 | 000 | 000 |\n'
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
        exp_val='Phasers are damaged. Repairs are underway.'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Call for phasers
        phaser_controls()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
        # Assert the output matches the expected value
        self.assertEqual(exp_val, act_val)

    def test_phaser_controls_no_klingons(self):
        random.seed(1234567890)
        gm=game
        initialize_game()
        generate_sector()
        exp_val='There are no Klingon ships in this quadrant.'
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Call for phasers
        phaser_controls()
        # Get the captured output
        act_val = captured_output.getvalue().strip()
        # Reset the standard output
        sys.stdout = sys.__stdout__
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
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--3000): '
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
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--3000): '
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
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--3000): '
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
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--3000): '
        exp_val+='Firing phasers...\n'
        exp_val+='Klingon ship destroyed at sector [4,3].'
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
        command_prompt()
        # Redirect standard output to a buffer
        captured_output = StringIO()
        sys.stdout = captured_output
        # Fire phasers
        exp_val='Enter command: '
        exp_val+='Phasers locked on target.\n'
        exp_val+='Enter phaser energy (1--3000): '
        exp_val+='Firing phasers...\n'
        exp_val+='Hit ship at sector [4,3]. Klingon shield strength dropped to 170.\n'
        exp_val+='Enterprise hit by ship at sector [4,3]. No damage due to starbase shields.'
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

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in valid input of an integer
    @patch('sys.stdin', StringIO('7\n'))
    def test_input_int(self):
        exp_val=7
        act_val=input_int('Enter a valid integer number:')
        self.assertEqual(exp_val, act_val)

    # Apply a patch() decorator to replace keyboard input from user with a string.
    # The patch should result in an invalid input
    @patch('sys.stdin', StringIO('7.5\n'))
    def test_input_int(self):
        act_val=input_int('Enter a valid integer number:')
        self.assertFalse(act_val)


if __name__ == '__main__':
    unittest.main()
