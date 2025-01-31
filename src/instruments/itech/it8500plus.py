#!/usr/bin/env python
"""
Driver for the ITECH IT8500+ single input programmable load

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
"""

# IMPORTS #####################################################################

from instruments.units import ureg as u

from instruments.abstract_instruments import ProgrammableLoad
from instruments.util_fns import enum_property, unitful_property, bool_property


# CLASSES #####################################################################


class IT8500plus(ProgrammableLoad, ProgrammableLoad.Channel):
    """
    The IT8500+ is a single input programmable load.

    Because it is a single channel input, this object inherits from both
    ProgrammableLoad and ProgrammableLoad.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.itech.IT8500plus.open_visa(<visa-adress>)
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

    voltage_range = unitful_property(
        "VOLT:RANG",
        u.volt,
        doc="""
        Gets/sets the input voltage range.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current_range = unitful_property(
        "CURR:RANG",
        u.amp,
        doc="""
        Gets/sets the input current range.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current_slew = unitful_property(
        "CURR:SLEW",
        u.amp / u.microsecond,
        doc="""
        Gets/sets the input current slew rate in both directions.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A/µs}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current_slew_rise = unitful_property(
        "CURR:SLEW:RISE",
        u.amp / u.microsecond,
        doc="""
        Gets/sets the input current slew rate in the positive direction.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A/µs}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current_slew_fall = unitful_property(
        "CURR:SLEW:FALL",
        u.amp / u.microsecond,
        doc="""
        Gets/sets the input current slew rate in the negative direction.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A/µs}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    overcurrent = unitful_property(
        "CURR:PROT",
        u.amp,
        doc="""
        Gets/sets the overcurrent protection setting in amps.

        Note there is no bounds checking on the value specified.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~pint.Quantity`
        """,
    )

    overpower = unitful_property(
        "POW:PROT",
        u.watt,
        doc="""
        Gets/sets the overpower protection setting in watts.

        Note there is no bounds checking on the value specified.

        :units: :math:`\\text{W}` (watts)
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

    mode = enum_property(
        command="MODE",
        enum=ProgrammableLoad.Channel.Mode,
        doc="""
        Gets/sets the input mode of the programmable load

        :type: `IT8500plus.Mode`
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

    remote_sense = bool_property(
        "SYST:SENS",
        inst_true="1",
        inst_false="0",
        doc="""
        Gets/sets the remote sense/compensation status.

        This is a toggle setting. True will turn the remote sense on
        while False will turn it off.

        :type: `bool`
        """,
    )

    @property
    def cv_current_limit(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the CV current limit is not supported.")

    @mode.setter
    def cv_current_limit(self, newval):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the CV current limit is not supported.")

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        # Set termination character
        self.terminator = "\n"

        # Set instrument to remote mode
        self.sendcmd("SYST:REM")
        self._remote_mode = True

    def reset(self):
        """
        Reset overvoltage, overcurrent, and overpower errors to resume operation.
        """
        self.sendcmd("CURR:PROT:CLE")
        self.sendcmd("POW:PROT:CLE")
        self.sendcmd("VOLT:PROT:CLE")

    @property
    def channel(self):
        """
        Return the channel (which in this case is the entire instrument, since
        there is only 1 channel on the IT8500+.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            IT8500plus object.
        """
        return (self,)
