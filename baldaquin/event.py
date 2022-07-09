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

import random
import sys
import time
from typing import Any

from loguru import logger

from baldaquin.buf import FIFO, CircularBuffer
from baldaquin._qt import QtCore



class EventHandlerBase(QtCore.QRunnable):

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
        dt = random.expovariate(self._rate)
        self._trigger_id += 1
        self._timestamp = time.time() - self._start_time
        time.sleep(dt)
        return (self._trigger_id, self._timestamp)
