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

"""Mock data strtuctures for testing purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import struct
import time
from typing import Any

from loguru import logger

from baldaquin.app import UserApplicationBase
from baldaquin.config import ConfigurationBase
from baldaquin.event import EventBase, EventHandlerBase
from baldaquin.runctrl import RunControlBase
from baldaquin.mock import MOCK_PROJECT_NAME


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



class MockEventServer:

    """Mock event server for testing purposes.

    This is serving events Poisson-distributed in time, with a constant
    underlying rate. (Note that the timing is achieved via simple calls to
    ``time.sleep()``, and it goes without saying that the time distribution
    of the events is not guaranteed to be accurate, especially at high
    input rates.)

    Arguments
    ---------
    file_path : str
        The path to the output file.

    rate : float
        The average event rate.
    """

    def __init__(self, rate : float = 10., pha_mu : float = 1000., pha_sigma : float = 50.):
        """Constructor.
        """
        self.rate = rate
        self.pha_mu = pha_mu
        self.pha_sigma = pha_sigma
        self.trigger_id = -1
        self.start_time = time.time()

    def next(self) -> Any:
        """Overloaded method.
        """
        time.sleep(random.expovariate(self.rate))
        event = MockEvent.random(self.trigger_id, self.start_time, self.pha_mu, self.pha_sigma)
        self.trigger_id += 1
        return event.pack()



class MockUserAppConfiguration(ConfigurationBase):

    """Configuration structure for the mock uaser app.
    """

    TITLE = 'Mock application configuration'
    PARAMETER_SPECS = (
        ('rate', 'float', 100., 'Target event rate', 'Hz', '.1f', dict(min=0.)),
        ('pha_mu', 'float', 1000., 'Average pulse height', 'ADC counts', '.1f', dict(min=100.)),
        ('pha_sigma', 'float', 50., 'Pulse height rms', 'ADC counts', '.1f', dict(min=10.))
    )



class MockEventHandler(EventHandlerBase):

    """Mock event handler for testing purpose.
    """

    #def process_event(self):
    #    """
    #    """
    #    pass



class MockUserApplication(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    EVENT_HANDLER_CLASS = MockEventHandler

    def __init__(self, rate : float = 10., pha_mu : float = 1000., pha_sigma : float = 50.):
        """Constructor.
        """
        super().__init__()
        self._event_server = MockEventServer(rate, pha_mu, pha_sigma)

    def process_event(self):
        """Overloaded method.
        """
        evt = self._event_server.next()
        logger.debug(evt)
        return evt


class MockRunControl(RunControlBase):

    """
    """

    PROJECT_NAME = MOCK_PROJECT_NAME



if __name__ == '__main__':
    """
    import os
    from baldaquin import BALDAQUIN_DATA
    app = MockUserApplication()
    app.start(os.path.join(BALDAQUIN_DATA, 'test_app.bin'))
    time.sleep(5)
    app.stop()
    """
    rc = MockRunControl()
    app = MockUserApplication()
    rc.load_user_application(app)
    rc.set_stopped()
    rc.set_running()
