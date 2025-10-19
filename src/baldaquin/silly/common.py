# Copyright (C) 2022--2024 the baldaquin team.
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

"""Silly DAQ application for testing purposes.
"""

# Need to understand why this is
# from __future__ import annotations

import random
import time

from baldaquin import silly
from baldaquin.app import UserApplicationBase
from baldaquin.config import UserApplicationConfiguration
from baldaquin.event import EventHandlerBase
from baldaquin.gui import MainWindow
from baldaquin.pkt import FixedSizePacketBase, Format, packetclass
from baldaquin.runctrl import RunControlBase


@packetclass
class SillyPacket(FixedSizePacketBase):

    """Silly packet definition.
    """

    trigger_id: Format.UNSIGNED_LONG
    seconds: Format.UNSIGNED_LONG
    microseconds: Format.UNSIGNED_LONG
    pha: Format.UNSIGNED_LONG

    def __post_init__(self) -> None:
        """Post-initialization.
        """
        self.timestamp = self.seconds + 1.e-6 * self.microseconds


class SillyServer:

    """Silly event server for testing purposes.

    This is serving events Poisson-distributed in time, with a constant
    underlying rate.
    """

    def __init__(self, rate: float = 5., pha_mean: float = 1000.,
                 pha_sigma: float = 50.) -> None:
        """Constructor.
        """
        self.rate = rate
        self.pha_mean = pha_mean
        self.pha_sigma = pha_sigma
        self.trigger_id = -1
        self.start_time = time.time()

    def setup(self, rate: float, pha_mean: float, pha_sigma: float) -> None:
        """Setup the silly event server.

        Do we really want to pass a configuration object, here?
        """
        self.rate = rate
        self.pha_mean = pha_mean
        self.pha_sigma = pha_sigma
        self.trigger_id = -1
        self.start_time = time.time()

    def next(self) -> bytes:
        """Return the next packet data.
        """
        self.trigger_id += 1
        time.sleep(random.expovariate(self.rate))
        timestamp = time.time() - self.start_time
        seconds = int(timestamp)
        microseconds = round((timestamp - seconds) * 1.e6)
        pha = round(random.gauss(self.pha_mean, self.pha_sigma))
        packet = SillyPacket(self.trigger_id, seconds, microseconds, pha)
        return packet.pack()


class SillyEventHandler(EventHandlerBase):

    """Silly event handler for testing purpose.
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self.server = SillyServer()

    def read_packet(self):
        """Overloaded method.
        """
        return self.server.next()


class SillyConfiguration(UserApplicationConfiguration):

    """Configuration structure for the mock user app.
    """

    _PARAMETER_SPECS = (
        ("rate", float, 5., "Target event rate", "Hz", ".1f", dict(min=0.)),
        ("pha_mean", float, 1000., "Mean pulse height", "ADC counts", ".1f",
            dict(min=500., max=10000.)),
        ("pha_sigma", float, 50., "Pulse height rms", "ADC counts", ".1f", dict(min=10.))
    )


class SillyUserApplicationBase(UserApplicationBase):

    """Base class for a silly user application.
    """

    EVENT_HANDLER_CLASS = SillyEventHandler

    def configure(self):
        """Overloaded method.
        """
        section = self.configuration.application_section()
        rate = section.value("rate")
        pha_mean = section.value("pha_mean")
        pha_sigma = section.value("pha_sigma")
        self.event_handler.server.setup(rate, pha_mean, pha_sigma)


class SillyRunControl(RunControlBase):

    """Silly run control for testing purposes.
    """

    _PROJECT_NAME = silly.PROJECT_NAME


class SillyMainWindow(MainWindow):

    """Mock main window for testing purposes.
    """

    _PROJECT_NAME = silly.PROJECT_NAME
