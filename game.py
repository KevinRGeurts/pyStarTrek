# standard imports
import logging

# local imports
from quadrant import Quadrant


class Game():
    """
    This class represents the Star Trek game state and contains all the variables needed to track the game.
    """

    def __init__(self):
        """
        Somewhat ironically, does not initialize the game to a playable state.
        """
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

    def setup_logging(self):
        """
        This method configures logging. It should be called ahead of any calls to startrek.run(...) to ensure the expected behavior
        of logging. Though failure to do so should not be breaking.
        :return: None
        """
        # Create a logger with name 'startrek_logger'. This is NOT the root logger, which is one level up from here, and has no name.
        # This logger is currently intended to handle everything that isn't navigation data going to file.
        logger = logging.getLogger('startrek_logger')
        # This is the threshold level for the logger itself, before it will pass to any handlers, which can have their own threshold.
        # Should be able to control here what the stream handler receives and thus what ends up going to stderr.
        # Use this key for now:
        #   DEBUG = debug messages sent to this logger will end up on stderr (e.g., ...)
        #   INFO = info messages sent to this logger will end up on stderr (e.g., ...)
        logger.setLevel(logging.INFO)
        # Set up this highest level below root logger with a stream handler
        sh = logging.StreamHandler()
        # Set the threshold for the stream handler itself, which will come into play only after the logger threshold is met.
        sh.setLevel(logging.DEBUG)
        # Add the stream handler to the logger
        logger.addHandler(sh)
    
        # Create the new logger that will handle navigation data going to file.
        # Create it as a child of the logger, 'blackjack_logger'
        logger = logging.getLogger('startrek_logger.navigation_logger')
        # Set the logger's level to INFO. If this is left at the NOTSET default, then all messages would be sent to parent
        # (Except that propagate is set to False below.) 
        logger.setLevel(logging.INFO)
        # Don't propagate to parents from this logger
        logger.propagate = False
        
        return None

    def setup_navigation_logging_file_handler(self, logpath):
        """
        This method configures a file handler for logger 'startrek_logger.navigation_logger'.
        It is optional to call this, but it should be called after calling the setup_logging() method.
        :parameter logpath: The path and name of the file for logging navigation data, string with '\\' escaped
        :return: the logger.fileHandler
        """
        # Get the navigation data logger so we can add a file handler to it
        logger = logging.getLogger('startrek_logger.navigation_logger')
        # Create a file handler to log events at this level of the logger hierarchy
        fh = logging.FileHandler(filename=logpath, mode='w')
        # Log an info message at this level of the logger, but note, since the file handler hasn't been added to the logger yet,
        # this message will not go into the logging file, which is good, since it is not navigation data
        msg = 'navigation data will be logged to file: ' + logpath
        logging.getLogger('startrek_logger').info(msg)
        # Set the file handler to log at INFO level, so navigation data needs to be injected to this logger wth logger.info(...)
        fh.setLevel(logging.INFO)
        # Create a formatter for navigation info, which just logs the info string itself, and add it to the file handler
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        # Add the file handler to the logger
        logger.addHandler(fh)
        # Add "header" information to the navigation data logging file
        # TODO: Decide what naviagtion data to log, and provide header information for that.
        # logger.info('%s,%s,%s', 'HAND', 'SHOW', 'CLASS' )
        
        return fh


class GameOptions():
    """
    This class represents the options for the Star Trek game. Typially these will get set by command line
    arguments, and then referenced as needed by the game.
    """
    def __init__(self):
        """
        """
        self.debugging = False
        self.play_with_ai = False
        self.logging = False
        self.cheat_no_damage = False


