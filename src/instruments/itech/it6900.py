#!/usr/bin/env python
"""
Driver for the ITECH IT6900 single output power supply

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
Adapted from HP6652A implementation by Wil Langford (wil.langford+instrumentkit@gmail.com)
"""

# IMPORTS #####################################################################


from instruments.units import ureg as u

from instruments.abstract_instruments import PowerSupply
from instruments.util_fns import unitful_property, bool_property


# CLASSES #####################################################################


class IT6900(PowerSupply, PowerSupply.Channel):
    """
    The IT6900 is a single output power supply.

    Because it is a single channel output, this object inherits from both
    PowerSupply and PowerSupply.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.itech.it6900.open_visa(<visa-adress>)
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

    display_mode = bool_property(
        "DISP",
        inst_true="ON",
        inst_false="OFF",
        doc="""
        Gets/sets the display mode.

        This is a toggle setting. True will turn the display on.  False
        will turn the display off

        .. seealso:: `~IT6900.display_text()`

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

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        # Set instrument to remote mode
        self.sendcmd("SYST:REM")
        self._remote_mode = True

    def reset(self):
        """
        Reset overvoltage and overcurrent errors to resume operation.
        """
        self.sendcmd("CURR:PROT:CLE")
        self.sendcmd("VOLT:PROT:CLE")

    def display_text(self, text_to_display):
        """
        Sends up to 12 (uppercase) alphanumerics to be sent to the
        front-panel LCD display.  Some punctuation is allowed, and
        can affect the number of characters allowed.  See the
        programming manual for the IT6900 for more details.

        Because the maximum valid number of possible characters is
        12 (counting the possible use of punctuation), the text will
        be truncated to 12 characters before the command is sent to
        the instrument.

        If an invalid string is sent, the command will fail silently.
        Any lowercase letters in the text_to_display will be converted
        to uppercase before the command is sent to the instrument.

        No attempt to validate punctuation is currently made.

        Because the string cannot be read back from the instrument,
        this method returns the actual string value sent.

        :param text_to_display: The text that you wish to have displayed
            on the front-panel LCD
        :type text_to_display: 'str'
        :return: Returns the version of the provided string that will
            be send to the instrument. This means it will be truncated to
            a maximum of 12 characters and changed to all upper case.
        :rtype: `str`
        """

        if len(text_to_display) > 12:
            text_to_display = text_to_display[:12]
        text_to_display = text_to_display.upper()

        self.sendcmd(f'DISP:TEXT "{text_to_display}"')

        return text_to_display

    def clear_text(self):
        """
        Clears the displayed text on the fron-panel VFD display of the
        instrument
        """

        self.sendcmd(f"DISP:TEXT:CLE")

    @property
    def channel(self):
        """
        Return the channel (which in this case is the entire instrument, since
        there is only 1 channel on the IT6900.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            IT6900 object.
        """
        return (self,)
