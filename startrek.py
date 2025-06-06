# standard imports
from math import pi, cos, sin
import random
import strings
import sys

# local imports
from quadrant import Quadrant
from utilities import print_strings, compute_direction, distance, input_double
from gob import Gob
from action_manager import ActionManager
import glob_vars # Leave this import like this exactly, so that global variables in it are actually global.
import startrek_actions  # Leave this import like this exactly, so that a circle import is avoided with startrek.py.
import startrek_goals

class SectorType():

    def __init__(self):
        self.empty, self.star, self.klingon, self.enterprise, self.starbase = 1, 2, 3, 4, 5

sector_type = SectorType()


class KlingonShip():

    def __init__(self):
        self.sector_x = 0
        self.sector_y = 0
        self.shield_level = 0


def run(game_ai=False):
    """
    Main entry point for playing a game, either manually, or using game AI.
    :param game_ai: If True, run the game using AI. If False, run the game manually.
    :return: None
    """
    game=glob_vars.the_game
    print_strings(strings.titleStrings)
    initialize_game()
    print_mission()
    generate_sector()
    print_strings(strings.commandStrings)
    while game.energy > 0 and not game.destroyed and game.klingons > 0 and game.time_remaining > 0:
        if not game_ai:
            command_prompt()
        else:
            # TODO: Implement ai game play entry point.
            play_ai_game()
            return None
            # raise NotImplementedError("Game AI not implemented yet.")
        print_game_status()
    return None


def play_ai_game():
    """
    Play the game using AI.
    """
    gob = Gob()
    gob.add_goal(startrek_goals.SurviveGoal())
    gob.add_goal(startrek_goals.FindKlingonShipGoal())
    # Note that the following action is problematic, in that at this point we would not know which quadrant
    # to navigate to.
    act1=startrek_actions.NavigateToQuadrantAction(expiry_time=10, qx=1, qy=6)
    gob.add_action(act1)
    act2=startrek_actions.RaiseShieldsAction(expiry_time=10, priority=10, shield_energy=500)
    gob.add_action(act2)
    # Should select the navigate, since we are in no danger yet.
    bestAct = gob.chooseAction()
    mgr = ActionManager()
    mgr.scheduleAction(bestAct)
    mgr.execute()
    # Should have brought us to quadrant with Klingon ship.
    # Should select to raise sheilds
    bestAct = gob.chooseAction()
    mgr.scheduleAction(bestAct)
    mgr.execute()
    mgr.execute()  # This should raise the shields.


def print_game_status():
    game=glob_vars.the_game
    if game.destroyed:
        print("MISSION FAILED: ENTERPRISE DESTROYED!!!")
        print
        print
        print
    elif game.energy == 0:
        print("MISSION FAILED: ENTERPRISE RAN OUT OF ENERGY.")
        print
        print
        print
    elif game.klingons == 0:
        print("MISSION ACCOMPLISHED: ALL KLINGON SHIPS DESTROYED. WELL DONE!!!")
        print
        print
        print
    elif game.time_remaining == 0:
        print("MISSION FAILED: ENTERPRISE RAN OUT OF TIME.")
        print
        print
        print


def command_prompt():
    command = input("Enter command: ").strip().lower()
    print
    if command == "nav":
        output = navigation()
        print_strings(output)
    elif command == "srs":
        scan_res = short_range_scan()
        print_strings(scan_res)
    elif command == "lrs":
        scan_res = long_range_scan()
        print_strings(scan_res)
    elif command == "pha":
        output = phaser_controls()
        print_strings(output)
    elif command == "tor":
        output = torpedo_control()
        print_strings(output)
    elif command == "she":
        output = shield_controls()
        print_strings(output)
    elif command == "com":
        computer_controls()
    elif command.startswith('qui') or command.startswith('exi'):
        exit()
    else:
        print_strings(strings.commandStrings)


def computer_controls():
    game=glob_vars.the_game
    if game.computer_damage > 0:
        print("The main computer is damaged. Repairs are underway.")
        print
        return
    print_strings(strings.computerStrings)
    command = input("Enter computer command: ").strip().lower()
    if command == "rec":
        display_galactic_record()
    elif command == "sta":
        display_status()
    elif command == "tor":
        photon_torpedo_calculator()
    elif command == "bas":
        starbase_calculator()
    elif command == "nav":
        navigation_calculator()
    else:
        print
        print("Invalid computer command.")
        print
    induce_damage(4)


def navigation_calculator():
    game=glob_vars.the_game
    print
    print("Enterprise located in quadrant [%s,%s]." % (game.quadrant_x + 1, game.quadrant_y + 1))
    print
    quad_x = input_double("Enter destination quadrant X (1--8): ")
    if quad_x is False or quad_x < 1 or quad_x > 8:
        print("Invalid X coordinate.")
        print
        return
    quad_y = input_double("Enter destination quadrant Y (1--8): ")
    if quad_y is False or quad_y < 1 or quad_y > 8:
        print("Invalid Y coordinate.")
        print
        return
    print
    qx = int(quad_x) - 1
    qy = int(quad_y) - 1
    if qx == game.quadrant_x and qy == game.quadrant_y:
        print("That is the current location of the Enterprise.")
        print
        return
    print("Direction: {0:1.2f}".format(compute_direction(game.quadrant_x, game.quadrant_y, qx, qy)))
    print("Distance:  {0:2.2f}".format(distance(game.quadrant_x, game.quadrant_y, qx, qy)))
    print


def starbase_calculator():
    game=glob_vars.the_game
    print
    if game.quadrants[game.quadrant_y][game.quadrant_x].starbase:
        print("Starbase in sector [%s,%s]." % (game.starbase_x + 1, game.starbase_y + 1))
        print("Direction: {0:1.2f}".format(
            compute_direction(game.sector_x, game.sector_y, game.starbase_x, game.starbase_y))
        )
        print("Distance:  {0:2.2f}".format(distance(game.sector_x, game.sector_y, game.starbase_x, game.starbase_y) / 8))
    else:
        print("There are no starbases in this quadrant.")
    print


def photon_torpedo_calculator():
    game=glob_vars.the_game
    print
    if len(game.klingon_ships) == 0:
        print("There are no Klingon ships in this quadrant.")
        print
        return

    for ship in game.klingon_ships:
        text = "Direction {2:1.2f}: Klingon ship in sector [{0},{1}]."
        print(text.format(
            ship.sector_x + 1, ship.sector_y + 1,
            compute_direction(game.sector_x, game.sector_y, ship.sector_x, ship.sector_y)))
    print


def display_status():
    game=glob_vars.the_game
    print
    print("               Time Remaining: {0}".format(game.time_remaining))
    print("      Klingon Ships Remaining: {0}".format(game.klingons))
    print("                    Starbases: {0}".format(game.starbases))
    print("           Warp Engine Damage: {0}".format(game.navigation_damage))
    print("   Short Range Scanner Damage: {0}".format(game.short_range_scan_damage))
    print("    Long Range Scanner Damage: {0}".format(game.long_range_scan_damage))
    print("       Shield Controls Damage: {0}".format(game.shield_control_damage))
    print("         Main Computer Damage: {0}".format(game.computer_damage))
    print("Photon Torpedo Control Damage: {0}".format(game.photon_damage))
    print("                Phaser Damage: {0}".format(game.phaser_damage))
    print


def display_galactic_record():
    game=glob_vars.the_game
    print
    sb = ""
    print("-------------------------------------------------")
    for i in range(8):
        for j in range(8):
            sb += "| "
            klingon_count = 0
            starbase_count = 0
            star_count = 0
            quadrant = game.quadrants[i][j]
            if quadrant.scanned:
                klingon_count = quadrant.klingons
                starbase_count = 1 if quadrant.starbase else 0
                star_count = quadrant.stars
            sb = sb + \
                "{0}{1}{2} ".format(klingon_count, starbase_count, star_count)
        sb += "|"
        print(sb)
        sb = ""
        print("-------------------------------------------------")
    print


def phaser_controls():
    """
    Entry point for full phaser control algorithm.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    ret_val=[] # list of strings
    (possible,output) = _phaser_control_precheck()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    else:
        # TODO: Try to clean up this hack, which is used to ensure that "Phasers locked on target." is printed
        # before phaser energy level is requested. 
        print_strings(ret_val)
        ret_val.clear()
    (possible, output, phaser_energy) = _phaser_controls_input()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    (output, ships_destroyed) = _phaser_controls_fire(phaser_energy)
    for i in output:
        ret_val.append(i)
    return ret_val


def _phaser_control_precheck():
    """
    Check that firing phasers is possible.
    :return: Tuple (Is it possible to fire phasers True/False, list of strings to be printed), as tuple (boolean, list of strings)
    """
    game=glob_vars.the_game
    output=[] # list of strings
    possible=True
    if game.phaser_damage > 0:
        possible=False
        output.append("Phasers are damaged. Repairs are underway.")
        output.append("")
    elif len(game.klingon_ships) == 0:
        possible=False
        output.append("There are no Klingon ships in this quadrant.")
        output.append("")
    else:
        output.append("Phasers locked on target.")
    return (possible, output)


def _phaser_controls_input():
    """
    Get input requrired to fire phasers.
    :return: Tuple (Is it possible to fire phasers True/False, list of strings to be printed, phaser energy level),
                as tuple (boolean, list of strings, float)
    """
    game=glob_vars.the_game
    possible=True
    output=[] # list of strings
    phaser_energy = input_double("Enter phaser energy (1--{0}): ".format(game.energy))
    if not phaser_energy or phaser_energy < 1 or phaser_energy > game.energy:
        possible=False
        output.append("Invalid energy level.")
        output.append("")
    return (possible, output, phaser_energy)


def _phaser_controls_fire(phaser_energy):
    """
    Actually fire the phasers.
    :parameter phaser_energy: Amount of energy to fire phasers with, float
    :return: Tuple (List of strings to be printed, Numnber of destroyed klingon ships), as type
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    ret_val.append("")
    ret_val.append("Firing phasers...")
    destroyed_ships = []
    for ship in game.klingon_ships:
        game.energy -= int(phaser_energy)
        if game.energy < 0:
            game.energy = 0
            break
        dist = distance(game.sector_x, game.sector_y, ship.sector_x, ship.sector_y)
        delivered_energy = phaser_energy * (1.0 - dist / 11.3)
        ship.shield_level -= int(delivered_energy)
        if ship.shield_level <= 0:
            ret_val.append("Klingon ship destroyed at sector [{0},{1}].".format(ship.sector_x + 1, ship.sector_y + 1))
            destroyed_ships.append(ship)
        else:
            ret_val.append("Hit ship at sector [{0},{1}]. Klingon shield strength dropped to {2}.".format(
                ship.sector_x + 1, ship.sector_y + 1, ship.shield_level
            ))
    for ship in destroyed_ships:
        game.quadrants[game.quadrant_y][game.quadrant_x].klingons -= 1
        game.klingons -= 1
        game.sector[ship.sector_y][ship.sector_x] = sector_type.empty
        game.klingon_ships.remove(ship)
    if len(game.klingon_ships) > 0:
        ret_val.append("")
        (output,something)=klingons_attack()
        for i in output:
            ret_val.append(i)
    ret_val.append("")
    return (ret_val, len(destroyed_ships))


def shield_controls():
    """
    Entry point for full shield control algorithm.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    ret_val=[] # list of strings
    (possible,output) = _shield_controls_precheck()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    else:
        # TODO: Try to clean up this hack, which is used to ensure that shield command options are printed
        # before shield command is requested. 
        print_strings(ret_val)
        ret_val.clear()
    (possible, output, she_add, energy_xfer) = _shield_controls_input()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    output = _shield_controls_adjust(she_add, energy_xfer)
    for i in output:
        ret_val.append(i)
    return ret_val

def _shield_controls_precheck():
    """
    Check that adjusting shields is possible.
        :return: Tuple (Is it possible to adjust shields True/False, list of strings to be printed), as tuple (boolean, list of strings)
    """
    game=glob_vars.the_game
    output=[] # list of strings
    possible = True
    if game.shield_control_damage > 0:
        possible = False
        output.append("Shield control is damaged. Repairs are underway.")
    else:
        output.append("--- Shield Controls ----------------")
        output.append("add = Add energy to shields.")
        output.append("sub = Subtract energy from shields.")
    output.append("")
    return (possible, output)

def _shield_controls_input():
    """
    Get input required to adjust shields.
    :return: Tuple (Is it possible to adjust shields True/False, list of strings to be printed, shield command=add Ture/False, energy to transfer),
                as tuple (boolean, list of strings, boolean, float)
    """
    game=glob_vars.the_game
    possible=True
    output=[] # list of strings
    she_add=None
    energy_xfer=0
    command = input("Enter shield control command: ").strip().lower()
    output.append("")
    if command == "add":
        she_add = True
        max_transfer = game.energy
    elif command == "sub":
        she_add = False
        max_transfer = game.shield_level
    else:
        possible=False
        output.append("Invalid command.")
        output.append("")
        return (possible, output, she_add, energy_xfer)
    energy_xfer = input_double(
        "Enter amount of energy (1--{0}): ".format(max_transfer))
    if not energy_xfer or energy_xfer < 1 or energy_xfer > max_transfer:
        possible=False
        output.append("Invalid amount of energy.")
        output.append("")
        return (possible, output, she_add, energy_xfer)
    output.append("")
    return (possible, output, she_add, energy_xfer)

def _shield_controls_adjust(she_add, energy_xfer):
    """
    Actually make the adjustment to the shields.
    :parameter she_add: Are we adding or subracting energy from the shields where True=adding, boolean
    :parameter energy_xfer: Amount of energy to transfer, float
    :return: List of strings to be printed, as list of strings
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    if she_add:
        game.energy -= int(energy_xfer)
        game.shield_level += int(energy_xfer)
    else:
        game.energy += int(energy_xfer)
        game.shield_level -= int(energy_xfer)
    ret_val.append("Shield strength is now {0}. Energy level is now {1}.".format(game.shield_level, game.energy))
    ret_val.append("")
    return ret_val

# TODO: Figure out what the True/False return value of this function is intended to indicate.
def klingons_attack():
    """
    Handle klingon ships attacking the Enterprise.
    :return: Tuple (List of strings to be printed, e.g., using print_strings(), bool?), as tuple
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    if len(game.klingon_ships) > 0:
        for ship in game.klingon_ships:
            if game.docked:
                ret_val.append("Enterprise hit by ship at sector [{0},{1}]. No damage due to starbase shields.".format(
                    ship.sector_x + 1, ship.sector_y + 1
                ))
            else:
                dist = distance(
                    game.sector_x, game.sector_y, ship.sector_x, ship.sector_y)
                delivered_energy = 300 * \
                    random.uniform(0.0, 1.0) * (1.0 - dist / 11.3)
                game.shield_level -= int(delivered_energy)
                if game.shield_level < 0:
                    game.shield_level = 0
                    game.destroyed = True
                ret_val.append("Enterprise hit by ship at sector [{0},{1}]. Shields dropped to {2}.".format(
                    ship.sector_x + 1, ship.sector_y + 1, game.shield_level
                ))
                if game.shield_level == 0:
                    return (ret_val,True)
        return (ret_val,True)
    return (ret_val,False)


def induce_damage(item):
    game=glob_vars.the_game
    if random.randint(0, 6) > 0:
        return
    damage = 1 + random.randint(0, 4)
    if item < 0:
        item = random.randint(0, 6)
    if item == 0:
        game.navigation_damage = damage
        print("Warp engines are malfunctioning.")
    elif item == 1:
        game.short_range_scan_damage = damage
        print("Short range scanner is malfunctioning.")
    elif item == 2:
        game.long_range_scan_damage = damage
        print("Long range scanner is malfunctioning.")
    elif item == 3:
        game.shield_control_damage = damage
        print("Shield controls are malfunctioning.")
    elif item == 4:
        game.computer_damage = damage
        print("The main computer is malfunctioning.")
    elif item == 5:
        game.photon_damage = damage
        print("Photon torpedo controls are malfunctioning.")
    elif item == 6:
        game.phaser_damage = damage
        print("Phasers are malfunctioning.")
    print


def repair_damage():
    game=glob_vars.the_game
    if game.navigation_damage > 0:
        game.navigation_damage -= 1
        if game.navigation_damage == 0:
            print("Warp engines have been repaired.")
        print
        return True
    if game.short_range_scan_damage > 0:
        game.short_range_scan_damage -= 1
        if game.short_range_scan_damage == 0:
            print("Short range scanner has been repaired.")
        print
        return True
    if game.long_range_scan_damage > 0:
        game.long_range_scan_damage -= 1
        if game.long_range_scan_damage == 0:
            print("Long range scanner has been repaired.")
        print
        return True
    if game.shield_control_damage > 0:
        game.shield_control_damage -= 1
        if game.shield_control_damage == 0:
            print("Shield controls have been repaired.")
        print
        return True
    if game.computer_damage > 0:
        game.computer_damage -= 1
        if game.computer_damage == 0:
            print("The main computer has been repaired.")
        print
        return True
    if game.photon_damage > 0:
        game.photon_damage -= 1
        if game.photon_damage == 0:
            print("Photon torpedo controls have been repaired.")
        print
        return True
    if game.phaser_damage > 0:
        game.phaser_damage -= 1
        if game.phaser_damage == 0:
            print("Phasers have been repaired.")
        print
        return True
    return False


def long_range_scan_precheck():
    """
    Check that long range scan is possible.
    :return: Tuple (Is it possible to perform long range scan True/False, list of strings to be printed), as tuple (boolean, list of strings)
    """
    game=glob_vars.the_game
    output=[] # list of strings
    possible = True
    if game.long_range_scan_damage > 0:
        possible = False
        output.append("Long range scanner is damaged. Repairs are underway.")
        output.append("")
    return (possible, output)


def long_range_scan():
    """
    Entry point for long range scan display.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    ret_val=[] # list of strings
    (possible, output) = long_range_scan_precheck()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    scanout = _long_range_scan()
    sb = ""
    ret_val.append("-------------------")
    for i in range(0,3):
        for j in range(0,3):
            sb += "| "
            sb = sb + scanout[i][j] + " "
        sb += "|"
        ret_val.append(sb)
        sb = ""
        ret_val.append("-------------------")
    ret_val.append("")
    return ret_val


def _long_range_scan():
    """
    Actually do the long range scan.
    :return: List of lists of strings, where each string is of the form 'xyz', where x is the number of klingons,
        y is the number of starbases, and z is the number of stars in the quadrant. Access the return value using
        ret_val[y-index][x-index], where y-index is the row index and x-index is the column index.
    """
    game=glob_vars.the_game
    ret_val = [[str() for _ in range(3)] for _ in range(3)] # list of lists of strings, i.e., ret_val[y-index][x-index]]
    ri=0
    rj=0
    for i in range(game.quadrant_y - 1, game.quadrant_y+2):  # quadrantY + 1 ?
        for j in range(game.quadrant_x - 1, game.quadrant_x+2):  # quadrantX + 1?
            klingon_count = 0
            starbase_count = 0
            star_count = 0
            if 0 <= i < 8 and 0 <= j < 8:
                quadrant = game.quadrants[i][j]
                quadrant.scanned = True
                klingon_count = quadrant.klingons
                starbase_count = 1 if quadrant.starbase else 0
                star_count = quadrant.stars
            ret_val[ri][rj] = "{0}{1}{2}".format(klingon_count, starbase_count, star_count)
            rj += 1
        rj = 0
        ri += 1
    return ret_val


def torpedo_control():
    """
    Entry point for full torpedo control algorithm.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    ret_val=[] # list of strings
    (possible,output) = _torpedo_control_precheck()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    (possible, output, direction) = _torpedo_controls_input()
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    output = _torpedo_control_launch(direction)
    for i in output:
        ret_val.append(i)
    return ret_val


def _torpedo_control_precheck():
    """
     Check that launching a torpedo is possible.
    :return: Tuple (Is it possible to launch torpedo True/False, list of strings to be printed), as tuple (boolean, list of strings)
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    possible = True
    if game.photon_damage > 0:
        possible = False
        ret_val.append("Photon torpedo control is damaged. Repairs are underway.")
        ret_val.append("")
    elif game.photon_torpedoes == 0:
        possible = False
        ret_val.append("Photon torpedoes exhausted.")
        ret_val.append("")
    elif len(game.klingon_ships) == 0:
        possible = False
        ret_val.append("There are no Klingon ships in this quadrant.")
        ret_val.append("")
    return (possible, ret_val)


def _torpedo_controls_input():
    """
    Get input requrired to launch torpedo.
    :return: Tuple (Is it possible to launch torpedo True/False, list of strings to be printed, torpedo direction),
                as tuple (boolean, list of strings, float)
    """
    possible=True
    output=[] # list of strings
    direction = input_double("Enter firing direction (1.0--9.0, 1=right,3=up,5=left,7=down): ")
    if not direction or direction < 1.0 or direction > 9.0:
        possible=False
        output.append("Invalid direction.")
        output.append("")
    return (possible, output, direction)


def _torpedo_control_launch(direction):
    """
    Actually launch the torpedo.
    :parameter direction: Direction in which to fire the torpedo, float
    :return: List of strings to be printed, e.g., using print_strings()
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    ret_val.append("")
    ret_val.append("Photon torpedo fired...")
    game.photon_torpedoes -= 1
    angle = -(pi * (direction - 1.0) / 4.0)
    if random.randint(0, 2) == 0:
        angle += (1.0 - 2.0 * random.uniform(0.0, 1.0) * pi * 2.0) * 0.03
    x = game.sector_x
    y = game.sector_y
    vx = cos(angle) / 20
    vy = sin(angle) / 20
    last_x = last_y = -1
    # new_x = game.sector_x
    # new_y = game.sector_y
    hit = False
    while x >= 0 and y >= 0 and round(x) < 8 and round(y) < 8:
        new_x = int(round(x))
        new_y = int(round(y))
        if last_x != new_x or last_y != new_y:
            ret_val.append("  [{0},{1}]".format(new_x + 1, new_y + 1))
            last_x = new_x
            last_y = new_y
        for ship in game.klingon_ships:
            if ship.sector_x == new_x and ship.sector_y == new_y:
                ret_val.append("Klingon ship destroyed at sector [{0},{1}].".format(ship.sector_x + 1, ship.sector_y + 1))
                game.sector[ship.sector_y][ship.sector_x] = sector_type.empty
                game.klingons -= 1
                game.klingon_ships.remove(ship)
                game.quadrants[game.quadrant_y][game.quadrant_x].klingons -= 1
                hit = True
                break  # break out of the for loop
        if hit:
            break  # break out of the while loop
        if game.sector[new_y][new_x] == sector_type.starbase:
            game.starbases -= 1
            game.quadrants[game.quadrant_y][game.quadrant_x].starbase = False
            game.sector[new_y][new_x] = sector_type.empty
            ret_val.append("The Enterprise destroyed a Federation starbase at sector [{0},{1}]!".format(new_x + 1, new_y + 1))
            hit = True
            break
        elif game.sector[new_y][new_x] == sector_type.star:
            ret_val.append("The torpedo was captured by a star's gravitational field at sector [{0},{1}].".format(
                new_x + 1, new_y + 1
            ))
            hit = True
            break
        x += vx
        y += vy
    if not hit:
        ret_val.append("Photon torpedo failed to hit anything.")
    if len(game.klingon_ships) > 0:
        print
        (output,something)=klingons_attack()
        for i in output:
            ret_val.append(i)
    ret_val.append("")
    return ret_val


def navigation():
    """
    Entry point for full navigation algorithm.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    ret_val=[] # list of strings
    (possible,output,max_warp_factor) = _navigation_precheck()
    for i in output:
        ret_val.append(i)
    if not possible:
        # TODO: Try to clean up this hack, which is used to ensure that "Warp engines damaged." is printed
        # before navigation course and warp factor are requested.
        print_strings(ret_val)
        ret_val.clear()
    (possible, output, course, warp_factor) = _navigation_input(max_warp_factor)
    for i in output:
        ret_val.append(i)
    if not possible:
        return ret_val
    output = _navigation(course, warp_factor)
    for i in output:
        ret_val.append(i)
    return ret_val


def _navigation_precheck():
    """
    Check that navigation is possible.
    :return: Tuple (Is it possible to navigate at full warp factor True/False, list of strings to be printed, maximum warp factor),
                as tuple (boolean, list of strings, float)
    """
    game=glob_vars.the_game
    output=[] # list of strings
    possible=True
    max_warp_factor = 8.0
    if game.navigation_damage > 0:
        possible=False
        max_warp_factor = 0.2 + random.randint(0, 8) / 10.0
        output.append("Warp engines damaged. Maximum warp factor: {0}".format(max_warp_factor))
        output.append("")
    return (possible, output, max_warp_factor)


def _navigation_input(max_warp_factor):
    """
    Get input required to navigate.
    :parameter max_warp_factor: Maximum warp factor, float
    :return: Tuple (Is navigation possible given requested course and warp factor True/False,
                    list of strings to be printed, course, warp_factor),
                as tuple (boolean, list of strings, float, float)
    """
    game=glob_vars.the_game
    output=[] # list of strings
    possible=True
    direction=None
    dist=None

    direction = input_double("Enter course (1.0--8.9, 1=right,3=up,5=left,7=down): ")
    if not direction or direction < 1.0 or direction > 9.0:
        possible=False
        output.append("Invalid course.")
        output.append("")
        return (possible, output, direction, None)

    dist = input_double("Enter warp factor (0.1--{0}): ".format(max_warp_factor))
    if not dist or dist < 0.1 or dist > max_warp_factor:
        possible=False
        output.append("Invalid warp factor.")
        output.append("")
        return (possible, output, direction, dist)

    output.append("")

    distance = dist*8
    energy_required = int(distance)
    if energy_required >= game.energy:
        possible=False
        output.append("Unable to comply. Insufficient energy to travel that speed.")
        output.append
        return (possible, output, direction, dist)
    
    return (possible, output, direction, dist)


# TODO: Return something to indicate hitting an obstacle.
def _navigation(course, warp_factor):
    """
    Actually navigate the Enterprise.
    :parameter course: Course to navigate, float
    :parameter warp_factor: Warp factor, float
    :return: List of strings to be printed, e.g., using print_strings()
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings

    direction = course
    dist = warp_factor*8
    energy_required = int(dist)
    ret_val.append("Warp engines engaged.")
    ret_val.append("")
    game.energy -= energy_required

    last_quad_x = game.quadrant_x
    last_quad_y = game.quadrant_y
    angle = -(pi * (direction - 1.0) / 4.0)
    x = game.quadrant_x * 8 + game.sector_x
    y = game.quadrant_y * 8 + game.sector_y
    dx = dist * cos(angle)
    dy = dist * sin(angle)
    vx = dx / 1000
    vy = dy / 1000
    # quad_x = quad_y = sect_x = sect_y = 0
    last_sect_x = game.sector_x
    last_sect_y = game.sector_y
    # Empty out the current game sector, from which navigation begins. This sector should always have contained
    # the Enterprise
    assert(game.sector[game.sector_y][game.sector_x] == sector_type.enterprise)
    game.sector[game.sector_y][game.sector_x] = sector_type.empty
    obstacle = False
    for i in range(999):
        x += vx
        y += vy
        quad_x = int(x//8)
        quad_y = int(y//8)
        if quad_x == game.quadrant_x and quad_y == game.quadrant_y:
            sect_x = int(x%8)
            sect_y = int(y%8)
            if game.sector[sect_y][sect_x] != sector_type.empty:
                game.sector_x = last_sect_x
                game.sector_y = last_sect_y
                game.sector[game.sector_y][game.sector_x] = sector_type.enterprise
                ret_val.append("Encountered obstacle within quadrant.")
                ret_val.append("")
                obstacle = True
                break
            last_sect_x = sect_x
            last_sect_y = sect_y

    if not obstacle:
        if x < 0:
            x = 0
        elif x > 63:
            x = 63
        if y < 0:
            y = 0
        elif y > 63:
            y = 63
        quad_x = int(x//8)
        quad_y = int(y//8)
        game.sector_x = int(x%8)
        game.sector_y = int(y%8)
        if quad_x != game.quadrant_x or quad_y != game.quadrant_y:
            game.quadrant_x = quad_x
            game.quadrant_y = quad_y
            generate_sector()
        else:
            game.quadrant_x = quad_x
            game.quadrant_y = quad_y
            game.sector[game.sector_y][game.sector_x] = sector_type.enterprise
    if is_docking_location(game.sector_y, game.sector_x):
        game.energy = 3000
        game.photon_torpedoes = 10
        game.navigation_damage = 0
        game.short_range_scan_damage = 0
        game.long_range_scan_damage = 0
        game.shield_control_damage = 0
        game.computer_damage = 0
        game.photon_damage = 0
        game.phaser_damage = 0
        game.shield_level = 0
        game.docked = True
    else:
        game.docked = False

    if last_quad_x != game.quadrant_x or last_quad_y != game.quadrant_y:
        game.time_remaining -= 1
        game.star_date += 1

    scan_res=short_range_scan()
    for i in scan_res:
        ret_val.append(i)

    if game.docked:
        ret_val.append("Lowering shields as part of docking sequence...")
        ret_val.append("Enterprise successfully docked with starbase.")
        ret_val.append("")
    else:
        if game.quadrants[game.quadrant_y][game.quadrant_x].klingons > 0 \
                and last_quad_x == game.quadrant_x and last_quad_y == game.quadrant_y:
            (output,something)=klingons_attack()
            for i in output:
                ret_val.append(i)
            ret_val.append("")
        elif not repair_damage():
            induce_damage(-1)

    return ret_val


def generate_sector():
    game=glob_vars.the_game
    quadrant = game.quadrants[game.quadrant_y][game.quadrant_x]
    starbase = quadrant.starbase
    stars = quadrant.stars
    klingons = quadrant.klingons
    game.klingon_ships = []
    for i in range(8):
        for j in range(8):
            game.sector[i][j] = sector_type.empty
    game.sector[game.sector_y][game.sector_x] = sector_type.enterprise
    while starbase or stars > 0 or klingons > 0:
        i = random.randint(0, 7)
        j = random.randint(0, 7)
        if is_sector_region_empty(i, j):
            if starbase:
                starbase = False
                game.sector[i][j] = sector_type.starbase
                game.starbase_y = i
                game.starbase_x = j
            elif stars > 0:
                game.sector[i][j] = sector_type.star
                stars -= 1
            elif klingons > 0:
                game.sector[i][j] = sector_type.klingon
                klingon_ship = KlingonShip()
                klingon_ship.shield_level = 300 + random.randint(0, 199)
                klingon_ship.sector_y = i
                klingon_ship.sector_x = j
                game.klingon_ships.append(klingon_ship)
                klingons -= 1


def is_docking_location(i, j):
    """
    :parameter i: Row in sector, or y-index in sector, 0-indexed, so valid range is 0..7
    :parameter j: Column in sector, or x-index in sector, 0-indexed, so valid range is 0..7
    """
    # NOTE: The two nested for loops will search a nine-sector box centered on (i,j), so that
    # the Enterprise will dock if it arrives in a sector that is adjacent to the starbase.
    for y in range(i - 1, i+2):  # i + 1?
        for x in range(j - 1, j+2):  # j + 1?
            if read_sector(y, x) == sector_type.starbase:
                return True
    return False


def is_sector_region_empty(i, j):
    """
    :parameter i: Row in sector, or y-index in sector, 0-indexed, so valid range is 0..7
    :parameter j: Column in sector, or x-index in sector, 0-indexed, so valid range is 0..7
    """
    # Imagine a 3X3 block of sectors centered around sector(row=i,col=j). This function checks that
    # sector (i,j) is empty, either the sector to the left or right is empty, and either the sector
    # to the upper-right or upper-left is emtpy. Notably, it does not check sectors to the lower-left or lower-right.
    # Assuming this is the desired behavior, then it prevents too much close packing when a sector is generated. 
    for y in range(i - 1, i+1):  # i + 1?
        if read_sector(y, j - 1) != sector_type.empty and read_sector(y, j + 1) != sector_type.empty:
            return False
    return read_sector(i, j) == sector_type.empty


def read_sector(i, j):
    """
    :parameter i: Row in sector, or y-index in sector, 0-indexed, so valid range is 0..7
    :parameter j: Column in sector, or x-index in sector, 0-indexed, so valid range is 0..7
    """
    game=glob_vars.the_game
    if i < 0 or j < 0 or i > 7 or j > 7:
        return sector_type.empty
    return game.sector[i][j]


def short_range_scan():
    """
    Return short range scan display.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    game=glob_vars.the_game
    ret_val=[] # List of strings of short range scan output
    if game.short_range_scan_damage > 0:
        ret_val.append("Short range scanner is damaged. Repairs are underway.")
        ret_val.append("")
    else:
        quadrant = game.quadrants[game.quadrant_y][game.quadrant_x]
        quadrant.scanned = True
        for i in print_sector(quadrant):
            ret_val.append(i)
    ret_val.append("")
    return ret_val


def print_sector(quadrant):
    """
    Return the sector content of a short range scan display.
    :return: List of strings to be printed, e.g., using print_strings()
    """
    game=glob_vars.the_game
    ret_val=[] # list of strings
    game.condition = "GREEN"
    if quadrant.klingons > 0:
        game.condition = "RED"
    elif game.energy < 300:
        game.condition = "YELLOW"

    sb = ""
    ret_val.append("X: 1  2  3  4  5  6  7  8")
    ret_val.append("Y:-=--=--=--=--=--=--=--=-          Region: {0}".format(quadrant.name))
    ret_val.append(print_sector_row('1 '+sb, 0, "           Quadrant: [{0},{1}]".format(game.quadrant_x + 1, game.quadrant_y + 1)))
    ret_val.append(print_sector_row('2 '+sb, 1, "             Sector: [{0},{1}]".format(game.sector_x + 1, game.sector_y + 1)))
    ret_val.append(print_sector_row('3 '+sb, 2, "           Stardate: {0}".format(game.star_date)))
    ret_val.append(print_sector_row('4 '+sb, 3, "     Time remaining: {0}".format(game.time_remaining)))
    ret_val.append(print_sector_row('5 '+sb, 4, "          Condition: {0}".format(game.condition)))
    ret_val.append(print_sector_row('6 '+sb, 5, "             Energy: {0}".format(game.energy)))
    ret_val.append(print_sector_row('7 '+sb, 6, "            Shields: {0}".format(game.shield_level)))
    ret_val.append(print_sector_row('8 '+sb, 7, "   Photon Torpedoes: {0}".format(game.photon_torpedoes)))
    ret_val.append("  -=--=--=--=--=--=--=--=-             Docked: {0}".format(game.docked))

    if quadrant.klingons > 0:
        ret_val.append("")
        ret_val.append("Condition RED: Klingon ship{0} detected.".format("" if quadrant.klingons == 1 else "s"))
        if game.shield_level == 0 and not game.docked:
            ret_val.append("Warning: Shields are down.")
    elif game.energy < 300:
        ret_val.append("")
        ret_val.append("Condition YELLOW: Low energy level.")
        game.condition = "YELLOW"

    return ret_val


def print_sector_row(sb, row, suffix):
    """
    Return one line of the sector content of a short range scan display.
    :return: Strings to be printed or appended into list of strings representing short scan of sector.
    """
    game=glob_vars.the_game
    for column in range(8):
        if game.sector[row][column] == sector_type.empty:
            sb += "   "
        elif game.sector[row][column] == sector_type.enterprise:
            sb += "<E>"
        elif game.sector[row][column] == sector_type.klingon:
            sb += "+K+"
        elif game.sector[row][column] == sector_type.star:
            sb += " * "
        elif game.sector[row][column] == sector_type.starbase:
            sb += ">S<"
    if suffix is not None:
        sb = sb + suffix
    return sb


def print_mission():
    game=glob_vars.the_game
    print("Mission: Destroy {0} Klingon ships in {1} stardates with {2} starbases.".format(
        game.klingons, game.time_remaining, game.starbases))
    print


def initialize_game():
    # globals
    game=glob_vars.the_game
    game.quadrant_x = random.randint(0, 7)
    game.quadrant_y = random.randint(0, 7)
    game.sector_x = random.randint(0, 7)
    game.sector_y = random.randint(0, 7)
    game.star_date = random.randint(0, 50) + 2250
    game.energy = 3000
    game.photon_torpedoes = 10
    game.time_remaining = 40 + random.randint(0, 9)
    game.klingons = 15 + random.randint(0, 5)
    game.starbases = 2 + random.randint(0, 2)
    game.destroyed = False
    game.navigation_damage = 0
    game.short_range_scan_damage = 0
    game.long_range_scan_damage = 0
    game.shield_control_damage = 0
    game.computer_damage = 0
    game.photon_damage = 0
    game.phaser_damage = 0
    game.shield_level = 0
    game.docked = False
    game.starbase_x = 0
    game.starbase_y = 0

    names = []
    for name in strings.quadrantNames:
        names.append(name)

    for i in range(8):
        for j in range(8):
            index = random.randint(0, len(names) - 1)
            quadrant = Quadrant()
            quadrant.name = names[index]
            quadrant.stars = 1 + random.randint(0, 7)
            game.quadrants[i][j] = quadrant
            del names[index]

    klingon_count = game.klingons
    starbase_count = game.starbases
    # Randomly place up to 3 klingon ships in quadrants until all klingon ships are placed.
    # Randomly place up to 1 starbase in quadrants until all starbases are placed.
    # Note that the intent is for all starbases to be placed in quadrants that also have at least 1 klingon.
    while klingon_count > 0 or starbase_count > 0:
        i = random.randint(0, 7)
        j = random.randint(0, 7)
        quadrant = game.quadrants[i][j]
        if not quadrant.starbase and starbase_count > 0:
            quadrant.starbase = True
            starbase_count -= 1
        if quadrant.klingons < 3:
            quadrant.klingons += 1
            klingon_count -= 1



if __name__ == '__main__':
    game_ai=False
    if len(sys.argv)>1:
        if sys.argv[1:].__contains__('/d'):
            # '/d' = Debug mode
            # Seed the random number generator.
            # Intended to sync game play with a unittest case.
            sv=1234567890
            random.seed(sv)
            print('Running in DEBUG mode...')
        if sys.argv[1:].__contains__('/ai'):
            # '/ai' = AI mode, where game AI will be used to automatically play the game
            game_ai=True
            print('Running in AI mode...')
    run(game_ai)
