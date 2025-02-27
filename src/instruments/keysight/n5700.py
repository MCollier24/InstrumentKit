#!/usr/bin/env python
"""
Driver for the Keysight N5700 series single output power supplies

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
"""

# IMPORTS #####################################################################


from enum import Enum
from instruments.units import ureg as u

from instruments.abstract_instruments import PowerSupply
from instruments.util_fns import unitful_property, bool_property, enum_property


# CLASSES #####################################################################


class N5700(PowerSupply, PowerSupply.Channel):
    """
    The N5700 is a single output power supply.

    Because it is a single channel output, this object inherits from both
    PowerSupply and PowerSupply.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.keysight.n5700.open_visa(<visa-adress>)
    >>> psu.voltage = 3 # Sets output voltage to 3V.
    >>> psu.output = True
    >>> psu.voltage
    array(3.0) * V
    >>> psu.voltage_sense < 5
    True
    >>> psu.output = False
    >>> psu.voltage_sense < 1
    True
    """

    # ENUMS ##

    class RLState(Enum):
        """
        Enum containg valid remote/local modes for the unit
        """

        REM = "REMote"
        LOC = "LOCal"
        RWLOCK = "RWLock"

    # PROPERTIES ##

    voltage = unitful_property(
        "VOLT",
        u.volt,
        doc="""
        Gets/sets the output voltage.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current = unitful_property(
        "CURR",
        u.amp,
        doc="""
        Gets/sets the output current.

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
        Gets the actual output voltage as measured by the sense wires.

        :units: :math:`\\text{V}` (volts)
        :rtype: `~pint.Quantity`
        """,
    )

    current_sense = unitful_property(
        "MEAS:CURR",
        u.amp,
        readonly=True,
        doc="""
        Gets the actual output current as measured by the sense wires.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~pint.Quantity`
        """,
    )

    overvoltage = unitful_property(
        "VOLT:PROT",
        u.volt,
        doc="""
        Gets/sets the overvoltage protection setting in volts.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~pint.Quantity`
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

    output = bool_property(
        "OUTP",
        inst_true="1",
        inst_false="0",
        doc="""
        Gets/sets the output status.

        This is a toggle setting. True will turn on the instrument output
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
    def mode(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the mode is not implemented.")

    @mode.setter
    def mode(self, newval):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the mode is not implemented.")

    rlstate = enum_property(
        command="SYST:COMM:RLST",
        enum=RLState,
        doc="""
        Gets/sets the remote/local mode of the power supply

        :type: `n5700.RLState`
        """,
    )

    remote_mode = bool_property(
        command="SYST:COMM:RLST",
        inst_true="REM",
        inst_false="LOC",
        doc="""
        Gets / sets the status of remote mode.
        """,
    )

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        self.remote_mode = True

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
        there is only 1 channel on the N5700.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            N5700 object.
        """
        return (self,)
