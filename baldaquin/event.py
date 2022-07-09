# Copyright (C) 2022 the baldaquin team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Event handler.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import struct
import time
from typing import Any

from baldaquin.buf import CircularBuffer
from baldaquin._qt import QtCore



class EventHandlerBase(QtCore.QRunnable):

    # pylint: disable=c-extension-no-member

    """Base class for an event handler.

    This is an abstract base class inheriting from ``QtCore.QRunnable``, owning
    a data buffer that can be used to cache data, and equipped with a binary flag
    that allows for syncronization.

    Arguments
    ---------
    file_path : str
        The path to the output file.

    buffer_class : type
        The class to be used to instantiate the event buffer object.

    kwargs : dict
        Keyword arguents for the data buffer creation.
    """

    def __init__(self, file_path : str, buffer_class : type = CircularBuffer, **kwargs) -> None:
        """Constructor.
        """
        super().__init__()
        self.buffer = buffer_class(file_path, **kwargs)
        self.__running = False

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def run(self) -> None:
        """Overloaded QRunnable method.
        """
        self.__running = True
        while self.__running:
            self.buffer.put_item(self.process_event())

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError



@dataclass
class MockEvent:

    """Mock event data structure for testing purposes.

    This is a minimal event stucture including a trigger identifier, a timestamp
    and a pulse-height value. The :meth:`pack() <baldaquin.event.MockEvent.pack()>`
    method returns a bytes object that can be written into a binary file,
    while the :meth:`unpack() <baldaquin.event.MockEvent.unpack()>` method does
    the opposite, i.e., it constructs an event object from its binary representation
    (the two are designed to round-trip).

    .. note::

       Although this is intended as a simple mock data structture for unit testing
       this is a perfectly legitimate data structure that could be used
       as an inspiration for real applications.

    Arguments
    ---------
    trigger_id : int
        The trigger identifier for the event.

    seconds : int
        The integer part of the timestamp in seconds.

    microseconds : int
        The fractional part of the timestamp in microseconds.

    pha : int
        The pulse height value.
    """

    # pylint: disable=invalid-name
    _FMT = 'llll'

    trigger_id : int
    seconds : int
    microseconds : int
    pha : int

    @classmethod
    def random(cls, trigger_id : int, start_time : float = 0., pha_mu : float = 1000.,
               pha_sigma : float = 50.) -> MockEvent:
        """Create a random event object on the fly.

        Note that the trigger identifier must be passed externally as this function
        has no notion of a global state. The timestamp is taken from the system
        time and the pha is randomly generated from a gaussian distribution.

        Arguments
        ---------
        trigger_id : int
            The trigger identifier for the event.

        start_time : float
            Origin for the timestamp (will be subtracted from the system time).

        pha_mu : float
            The mean of of the pha (gaussian) distribution.

        pha_sigma : float
            The sigma of of the pha (gaussian) distribution.
        """
        timestamp = time.time() - start_time
        seconds = int(timestamp)
        microseconds = round((timestamp - seconds) * 1.e6)
        pha = round(random.gauss(pha_mu, pha_sigma))
        return cls(trigger_id, seconds, microseconds, pha)

    def pack(self) -> bytes:
        """Pack the event for supporting binary output to file.
        """
        return struct.pack(self._FMT, self.trigger_id, self.seconds, self.microseconds, self.pha)

    @classmethod
    def unpack(cls, data : bytes) -> MockEvent:
        """Unpack some data into an event object.
        """
        return cls(*struct.unpack(cls._FMT, data))

    @classmethod
    def read_from_file(cls, input_file) -> MockEvent:
        """Read a single event from a file object open in binary mode.
        """
        return cls.unpack(input_file.read(32))



class MockEventHandler(EventHandlerBase):

    """Mock event handler for testing purposes.

    This is serving events Poisson-distributed in time, with a constant
    underlying rate. (Note that the timing is achieved via simple calls to
    ``time.sleep()``, and it goes without saying that the time distribution
    of the events is not guaranteed to be accurate, especially at high
    input rates.)

    Arguments
    ---------
    Arguments
    ---------
    file_path : str
        The path to the output file.

    rate : float
        The average event rate.

    kwargs : dict
        Keyword arguents for the data buffer creation.
    """

    def __init__(self, file_path : str, rate : float = 100., **kwargs):
        """Constructor.
        """
        super().__init__(file_path, CircularBuffer, **kwargs)
        self._rate = rate
        self._trigger_id = -1
        self._start_time = time.time()

    def process_event(self) -> Any:
        """Overloaded method.
        """
        time.sleep(random.expovariate(self._rate))
        event = MockEvent.random(self._trigger_id, self._start_time)
        self._trigger_id += 1
        return event.pack()
