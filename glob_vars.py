# TODO: Move into new file
class Quadrant():

    def __init__(self):
        self.name = ""
        self.klingons = 0
        self.stars = 0
        self.starbase = False
        self.scanned = False


# Move into new file
class Game():

    def __init__(self):
        self.star_date = 0
        self.time_remaining = 0
        self.energy = 0
        self.klingons = 0
        self.starbases = 0
        self.quadrant_x, self.quadrant_y = 0, 0
        self.sector_x, self.sector_y = 0, 0
        self.shield_level = 0
        self.navigation_damage = 0
        self.short_range_scan_damage = 0
        self.long_range_scan_damage = 0
        self.shield_control_damage = 0
        self.computer_damage = 0
        self.photon_damage = 0
        self.phaser_damage = 0
        self.photon_torpedoes = 0
        self.docked = False
        self.destroyed = False
        self.starbase_x, self.starbase_y = 0, 0
        self.quadrants = [[Quadrant() for _ in range(8)] for _ in range(8)]
        self.sector = [[int() for _ in range(8)] for _ in range(8)]
        self.klingon_ships = []

the_game = Game()

