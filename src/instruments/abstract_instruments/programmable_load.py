#!/usr/bin/env python
"""
Provides an abstract base class for programmable load instruments
"""

# IMPORTS #####################################################################

import abc
from enum import Enum

from instruments.abstract_instruments import Instrument

# CLASSES #####################################################################


class ProgrammableLoad(Instrument, metaclass=abc.ABCMeta):
    """
    Abstract base class for programmable load instruments.

    All applicable concrete instruments should inherit from this ABC to
    provide a consistent interface to the user.
    """

    class Channel(metaclass=abc.ABCMeta):
        """
        Abstract base class for programmable load input channels.

        All applicable concrete instruments should inherit from this ABC to
        provide a consistent interface to the user.
        """

        # ENUMS #
        class Mode(Enum):
            """
            Enum containg valid input modes for many programmable loads
            """

            cc = "CURRent"
            cv = "VOLTage"
            cp = "POWer"
            cr = "RESistance"

        # PROPERTIES #

        @property
        @abc.abstractmethod
        def mode(self):
            """
            Gets/sets the input mode for the programmable load channel. This is an
            abstract method.

            :type: `~enum.Enum`
            """

        @mode.setter
        @abc.abstractmethod
        def mode(self, newval):
            pass

        @property
        @abc.abstractmethod
        def voltage(self):
            """
            Gets/sets the input voltage for the programmable load channel. This is an
            abstract method.

            :type: `~pint.Quantity`
            """

        @voltage.setter
        @abc.abstractmethod
        def voltage(self, newval):
            pass

        @property
        @abc.abstractmethod
        def current(self):
            """
            Gets/sets the input current for the programmable load channel. This is an
            abstract method.

            :type: `~pint.Quantity`
            """

        @current.setter
        @abc.abstractmethod
        def current(self, newval):
            pass

        @property
        @abc.abstractmethod
        def current_range(self):
            """
            Gets/sets the input current range for the programmable load channel. This is an
            abstract method.

            :type: `~pint.Quantity`
            """

        @current.setter
        @abc.abstractmethod
        def current_range(self, newval):
            pass

        @property
        @abc.abstractmethod
        def input(self):
            """
            Gets/sets the input status for the programmable load channel. This is an
            abstract method.

            :type: `bool`
            """

        @input.setter
        @abc.abstractmethod
        def input(self, newval):
            pass

    # PROPERTIES #

    @property
    @abc.abstractmethod
    def channel(self):
        """
        Gets a channel object for the programmable load. This should use
        `~instruments.util_fns.ProxyList` to achieve this.

        This is an abstract method.

        :rtype: `ProgrammableLoad.Channel`
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def remote_mode(self):
        """
        Gets / sets the status of the instruments remote operation mode.

        :type: `bool`
        """

    @remote_mode.setter
    def remote_mode(self, newval: bool):
        pass
