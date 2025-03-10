#!/usr/bin/env python
"""
Driver for the Korad KEL10X single input programmable load

Originally contributed by Matthew Collier (matthew.collier@outlook.com)
"""

# IMPORTS #####################################################################

from instruments.units import ureg as u

from instruments.abstract_instruments import ProgrammableLoad
from instruments.util_fns import enum_property, unitful_property, bool_property


# CLASSES #####################################################################


class KEL10X(ProgrammableLoad, ProgrammableLoad.Channel):
    """
    The KEL10X is a single input programmable load.

    Because it is a single channel input, this object inherits from both
    ProgrammableLoad and ProgrammableLoad.Channel.

    Example usage:

    >>> import time
    >>> import instruments as ik
    >>> psu = ik.korad.KEL10X.open_visa(<visa-adress>)
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

    ## ENUM MAPPING ##
    MODE_MAP = {
        ProgrammableLoad.Mode.CC: "CC",
        ProgrammableLoad.Mode.CV: "CV",
        ProgrammableLoad.Mode.CR: "CR",
        ProgrammableLoad.Mode.CP: "CP",
        "CC": ProgrammableLoad.Mode.CC,
        "CV": ProgrammableLoad.Mode.CV,
        "CR": ProgrammableLoad.Mode.CR,
        "CP": ProgrammableLoad.Mode.CP,
    }

    # PROPERTIES ##

    voltage = unitful_property(
        ":VOLT",
        u.volt,
        format_code="{:d}V",
        doc="""
        Gets/sets the input voltage.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{V}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    current = unitful_property(
        ":CURR",
        u.amp,
        format_code="{:d}A",
        doc="""
        Gets/sets the input current.

        Note there is no bounds checking on the value specified.

        :units: As specified, or assumed to be :math:`\\text{A}` otherwise.
        :type: `float` or `~pint.Quantity`
        """,
    )

    voltage_sense = unitful_property(
        ":MEAS:VOLT",
        u.volt,
        readonly=True,
        doc="""
        Gets the actual input voltage as measured by the sense wires.

        :units: :math:`\\text{V}` (volts)
        :rtype: `~pint.Quantity`
        """,
    )

    current_sense = unitful_property(
        ":MEAS:CURR",
        u.amp,
        readonly=True,
        doc="""
        Gets the actual input current as measured by the sense wires.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~pint.Quantity`
        """,
    )

    power_sense = unitful_property(
        ":MEAS:POW",
        u.watt,
        readonly=True,
        doc="""
        Gets the actual input power as measured by the sense wires.

        :units: :math:`\\text{A}` (amps)
        :rtype: `~pint.Quantity`
        """,
    )

    @property
    def current_range(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the current range is not supported.")
    
    @property
    def voltage_range(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the voltage range is not supported.")
    
    @property
    def cv_current_limit(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the CV current limit is not supported.")

    @property
    def cv_current_limit(self):
        """
        Unimplemented.
        """
        raise NotImplementedError("Setting the CV current limit is not supported.")

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
    def mode(self) -> ProgrammableLoad.Mode:
        mode_response = self.query(":FUNC ?")
        return self.MODE_MAP.get(mode_response)

    @mode.setter
    def mode(self, mode: ProgrammableLoad.Mode):
        self.sendcmd(f":FUNC {self.MODE_MAP.get(mode)}")

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

    remote_mode = bool_property(
        ":SYST:LOCK",
        inst_true="1",
        inst_false="0",
        doc="""
        Gets/sets the remote mode of the instrument.

        This is a toggle setting. True will set the instrument to remote
        operation while False will set it to local.

        :type: `bool`
        """,
    )

    remote_sense = bool_property(
        ":SYST:COMP",
        inst_true="1",
        inst_false="0",
        doc="""
        Gets/sets the remote sense/compensation status.

        This is a toggle setting. True will turn the remote sense on
        while False will turn it off.

        :type: `bool`
        """,
    )

    # METHODS ##
    def __init__(self, filelike):
        super().__init__(filelike)

        # Set instrument to remote mode
        self.remote_mode = True

    def reset(self):
        """
        Reset instrument.
        """
        self.sendcmd("*RST")

    @property
    def channel(self):
        """
        Return the channel (which in this case is the entire instrument, since
        there is only 1 channel on the KEL10X.)

        :rtype: 'tuple' of length 1 containing a reference back to the parent
            KEL10X object.
        """
        return (self,)
