#!/usr/bin/env python
"""
Driver for the Keysight EL3423A single input programmable load

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
"""

# IMPORTS #####################################################################

from enum import Enum
from instruments.units import ureg as u

from instruments.abstract_instruments import ProgrammableLoad
from instruments.util_fns import (
    ProxyList,
    enum_property,
    unitful_property,
    bool_property,
)


# CLASSES #####################################################################


class EL3423A(ProgrammableLoad):
    """
    The EL3423A is a dual input programmable load.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.keysight.EL3423A.open_visa(<visa-adress>)
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

    # ENUMS #
    class RLState(Enum):
        """
        Enum containg valid remote/local modes for the unit
        """

        REM = "REMote"
        LOC = "LOCal"
        RWLOCK = "RWLock"

    class Channel(ProgrammableLoad.Channel):

        def __init__(self, load, chan_idx):
            self._load = load
            self._idx = chan_idx + 1

        # PRIVATE METHODS #

        def sendcmd(self, cmd):
            """
            Function used to send a command to the instrument while wrapping
            the command with the neccessary identifier for the channel.

            :param str cmd: Command that will be sent to the instrument after
                being suffixed with the channel identifier
            """
            self._load.sendcmd(f"{cmd},(@{self._idx})")

        def query(self, cmd):
            """
            Function used to send a command to the instrument while wrapping
            the command with the neccessary identifier for the channel.

            :param str cmd: Command that will be sent to the instrument after
                being prefixed with the channel identifier
            :return: The result from the query
            :rtype: `str`
            """
            return self._load.query(f"{cmd} (@{self._idx})")

        # PROPERTIES ##
        voltage = unitful_property(
            command="VOLT",
            units=u.volt,
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

        current_slew_positive = unitful_property(
            "CURR:SLEW:POS",
            u.amp / u.microsecond,
            doc="""
            Gets/sets the input current slew rate in the positive direction.

            Note there is no bounds checking on the value specified.

            :units: As specified, or assumed to be :math:`\\text{A/µs}` otherwise.
            :type: `float` or `~pint.Quantity`
            """,
        )

        curr_slew_negative = unitful_property(
            "CURR:SLEW:NEG",
            u.amp / u.microsecond,
            doc="""
            Gets/sets the input current slew rate in the negative direction.

            Note there is no bounds checking on the value specified.

            :units: As specified, or assumed to be :math:`\\text{A/µs}` otherwise.
            :type: `float` or `~pint.Quantity`
            """,
        )

        cv_current_limit = unitful_property(
            "CURR:LIM",
            u.amp,
            doc="""
            Gets/sets the input maximum current in CV mode.

            Note there is no bounds checking on the value specified.

            :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
            :type: `float` or `~pint.Quantity`
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
            enum=ProgrammableLoad.Mode,
            doc="""
            Gets/sets the input mode of the programmable load

            :type: `ProgrammableLoad.Mode`
            """,
        )

        remote_sense = bool_property(
            "VOLT:SENS",
            inst_true="EXT",
            inst_false="INT",
            doc="""
        Gets/sets the remote sense/compensation status.

        This is a toggle setting. True will turn the remote sense on
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

    @property
    def channel(self):
        """
        Gets a specific channel on the EL3423A. The desired channel is accessed
        like one would access a list.

        Example usage:

        >>> import instruments as ik
        >>> el3423a = ik.kesysight.el3424a.open_visa(<visa_address>)
        >>> print(el3423a.channel[0].voltage)

        :return: A channel object for the EL3423A
        :rtype: `~el34234a.Channel`
        """
        return ProxyList(self, self.Channel, range(2))

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        self.remote_mode = True

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
        there is only 1 channel on the EL3423A.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            EL3423A object.
        """
        return (self,)
