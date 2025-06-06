# standard imports


# local imports


# TODO: Questionable if we need this class at all. Created it because it was in the Gaming AI book I'm reading.
class BlackboardDatum(object):
    """
    This class represents an item of data written to an AI decision making blackboard.
    """
    def __init__(self, datum_type, value):
        """
        Initialize the BlackboardDatum object.
        :param datum_type: The type of the datum, as str
        :param value: The value of the datum, as any type.
        """
        self._datum_type = datum_type
        self._value = value

    @property
    def datum_type(self):
        """
        Return the type of the datum.
        :return: The type of the datum, as str
        """
        return self._datum_type

    @property
    def value(self):
        """
        Return the value of the datum.
        :return: The value of the datum, as any type.
        """
        return self._value


