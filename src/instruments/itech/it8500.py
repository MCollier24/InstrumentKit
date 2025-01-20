#!/usr/bin/env python
"""
Driver for the ITECH IT8500 single input programmable load

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
"""

# IMPORTS #####################################################################

from enum import Enum

from instruments.units import ureg as u

from instruments.abstract_instruments import ProgrammableLoad
from instruments.util_fns import unitful_property, bool_property


# CLASSES #####################################################################


class IT8500(ProgrammableLoad, ProgrammableLoad.Channel):
    """
    The IT8500 is a single input programmable load.

    Because it is a single channel input, this object inherits from both
    ProgrammableLoad and ProgrammableLoad.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.itech.IT8500.open_visa(<visa-adress>)
    >>> psu.voltage = 3 # Sets input voltage to 3V.
    >>> psu.input = True
    >>> psu.voltage
    array(3.0) * V
    >>> psu.voltage_sense < 5
    True
    >>> psu.input = False
    >>> psu.voltage_sense < 1
    True
    """

    # ENUMS ##

    class Mode(Enum):
        """Enum containing valid input modes of the IT8500"""

        CC = "CURRent"
        CV = "VOLTage"
        CP = "POWer"
        CR = "RESistance"
        DYN = "DYNamic"
        LED = "LED"
        CI = "IMPedance"

        @classmethod
        def from_value(cls, value: str):
            for member in cls:
                if member.value == value:
                    return member

            raise ValueError(f"{value} is not a valid value for {cls.__name__}")

    # PROPERTIES ##

    voltage = unitful_property(
        "VOLT",
        u.volt,
        doc="""
        Gets/sets the input voltage.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current = unitful_property(
        "CURR",
        u.amp,
        doc="""
        Gets/sets the input current.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    voltage_sense = unitful_property(
        "MEAS:VOLT",
        u.volt,
        readonly=True,
        doc="""
        Gets the actual input voltage as measured by the sense wires.

        :units: :math:`\\text{V}` (volts)
        :rtype: `~pint.Quantity`
        """,
    )

    current_sense = unitful_property(
        "MEAS:CURR",
        u.amp,
        readonly=True,
        doc="""
        Gets the actual input current as measured by the sense wires.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~pint.Quantity`
        """,
    )

    overcurrent = unitful_property(
        "CURR:PROT",
        u.amp,
        doc="""
        Gets/sets the overcurrent protection setting in amps.

        Note there is no bounds checking on the value specified.

        :units: :math:`\\text{V}` (volts)
        :rtype: `~pint.Quantity`
        """,
    )

    input = bool_property(
        "INP",
        inst_true="1",
        inst_false="0",
        doc="""
        Gets/sets the input status.

        This is a toggle setting. True will turn on the instrument input
        while False will turn it off.

        :type: `bool`
        """,
    )

    @property
    def name(self):
        """
        The name of the connected instrument, as reported by the
        standard SCPI command ``*IDN?``.

        :rtype: `str`
        """
        idn_string = self.query("*IDN?")
        idn_list = idn_string.split(",")
        return " ".join(idn_list[:2])

    @property
    def mode(self) -> Mode:
        """
        Gets the operating mode of the instrument
        """
        return self.Mode.from_value(self.query("MODE?"))

    @mode.setter
    def mode(self, newval: Mode):
        """
        Sets the operating mode of the instrument
        """
        self.sendcmd(f"MODE {newval.value}")

    @property
    def remote_mode(self):
        """
        Gets / sets the status of remote mode.
        """
        return self._remote_mode

    @remote_mode.setter
    def remote_mode(self, newval: bool):
        if newval and not self._remote_mode:
            self._remote_mode = True
            self.sendcmd("SYST:REM")
        elif not newval and self._remote_mode:
            self._remote_mode = False
            self.sendcmd("SYST:LOC")

    @property
    def remote_sense(self):
        """
        Gets / sets the status of remote mode.
        """
        return self._remote_sense

    @remote_sense.setter
    def remote_sense(self, newval: bool):
        # Set to remote mode if necessary
        if not self._remote_mode:
            self.remote_mode = True

        # Enable remote sense
        if newval and not self._remote_sense:
            self._remote_sense = True
            self.sendcmd("SYST:SENS ON")
        elif not newval and self._remote_sense:
            self._remote_sense = False
            self.sendcmd("SYST:SENS OFF")

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        # Set instrument to remote mode
        self.sendcmd("SYST:LOC")
        self._remote_mode = False

        # Initilize remote sense state
        self.sendcmd("SYST:SENS OFF")
        self._remote_sense = False

    def reset(self):
        """
        Reset overvoltage and overcurrent errors to resume operation.
        """
        self.sendcmd("CURR:PROT:CLE")
        self.sendcmd("VOLT:PROT:CLE")

    @property
    def channel(self):
        """
        Return the channel (which in this case is the entire instrument, since
        there is only 1 channel on the IT8500.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            IT8500 object.
        """
        return (self,)
