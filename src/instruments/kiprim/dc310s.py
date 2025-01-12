#!/usr/bin/env python
"""
Driver for the Kiprim DC310S single output power supply

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
Adapted from HP6652A implementation by Wil Langford (wil.langford+instrumentkit@gmail.com)
"""

# IMPORTS #####################################################################


from instruments.units import ureg as u

from instruments.abstract_instruments import PowerSupply
from instruments.util_fns import unitful_property, bool_property


# CLASSES #####################################################################


class DC310S(PowerSupply, PowerSupply.Channel):
    """
    The DC310S is a single output power supply.

    Because it is a single channel output, this object inherits from both
    PowerSupply and PowerSupply.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.kiprim.DC310S.open_serial('/dev/ttyUSB0', 115200)
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

    # I don't know of any possible enumerations supported
    # by this instrument.

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
        "VOLT:LIM",
        u.volt,
        doc="""
        Gets/sets the overvoltage protection setting in volts.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    overcurrent = unitful_property(
        "CURR:LIM",
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

    # METHODS ##

    @property
    def channel(self):
        """
        Return the channel (which in this case is the entire instrument, since
        there is only 1 channel on the DC310S.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            DC310S object.
        """
        return (self,)
