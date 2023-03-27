# Copyright (C) 2022--2023 the baldaquin team.
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

"""Mock data strtuctures for testing purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Any

from loguru import logger

from baldaquin.buf import CircularBuffer
from baldaquin.gui import MainWindow
from baldaquin.event import EventBase, EventHandlerBase
from baldaquin.mock import MOCK_PROJECT_NAME
from baldaquin._qt import QtWidgets
from baldaquin.runctrl import RunControlBase


@dataclass
class MockEvent(EventBase):

    """Mock event data structure for testing purposes.

    This is a minimal event stucture including a trigger identifier, a timestamp
    and a pulse-height value.
    """

    FORMAT_STRING = '=llll'

    trigger_id : int
    seconds : int
    microseconds : int
    pha : int

    @classmethod
    def random(cls, trigger_id : int, start_time, pha_mean : float, pha_sigma) -> MockEvent:
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

        pha_mean : float
            The mean of of the pha (gaussian) distribution.

        pha_sigma : float
            The sigma of of the pha (gaussian) distribution.
        """
        timestamp = time.time() - start_time
        seconds = int(timestamp)
        microseconds = round((timestamp - seconds) * 1.e6)
        pha = round(random.gauss(pha_mean, pha_sigma))
        return cls(trigger_id, seconds, microseconds, pha)



class MockEventServer:

    """Mock event server for testing purposes.

    This is serving events Poisson-distributed in time, with a constant
    underlying rate. (Note that the timing is achieved via simple calls to
    ``time.sleep()``, and it goes without saying that the time distribution
    of the events is not guaranteed to be accurate, especially at high
    input rates.)
    """

    def __init__(self, rate : float = 1., pha_mean : float = 1000.,
        pha_sigma : float = 50.) -> None:
        """Constructor.
        """
        self.rate = rate
        self.pha_mean = pha_mean
        self.pha_sigma = pha_sigma
        self.trigger_id = -1
        self.start_time = time.time()

    def setup(self, rate : float, pha_mean : float, pha_sigma : float) -> None:
        """Setup the mock event server.

        This is setting all the class members that are relevant for the next() method.
        """
        self.rate = rate
        self.pha_mean = pha_mean
        self.pha_sigma = pha_sigma
        self.trigger_id = -1
        self.start_time = time.time()

    def next(self) -> Any:
        """Overloaded method.
        """
        self.trigger_id += 1
        time.sleep(random.expovariate(self.rate))
        event = MockEvent.random(self.trigger_id, self.start_time, self.pha_mean, self.pha_sigma)
        return event.pack()



class MockEventHandler(EventHandlerBase):

    """Mock event handler for testing purpose.
    """

    BUFFER_CLASS = CircularBuffer
    BUFFER_KWARGS = dict(max_size=20, flush_size=10, flush_interval=2.)

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self.event_server = MockEventServer()

    def setup_server(self, rate : float, pha_mean : float, pha_sigma : float) -> None:
        """Setup the event server.
        """
        self.event_server.setup(rate, pha_mean, pha_sigma)

    def process_event(self):
        """Overloaded method.
        """
        event_data = self.event_server.next()
        event = MockEvent.unpack(event_data)
        logger.debug(f'{event} <- {event_data}')
        return event_data



class MockRunControl(RunControlBase):

    """Mock run control for testing purposes.
    """

    PROJECT_NAME = MOCK_PROJECT_NAME



class MockMainWindow(MainWindow):

    """Mock main window for testing purposes.
    """

    PROJECT_NAME = MOCK_PROJECT_NAME
    # pylint: disable=c-extension-no-member

    def __init__(self, parent : QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        #self.add_logger_tab()
