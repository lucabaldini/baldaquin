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

"""Simplest possible mock application.
"""

from loguru import logger

from baldaquin.gui import bootstrap_window
from baldaquin.pkt import AbstractPacket
from baldaquin.silly import SILLY_APP_CONFIG
from baldaquin.silly.common import (
    SillyConfiguration,
    SillyMainWindow,
    SillyPacket,
    SillyRunControl,
    SillyUserApplicationBase,
)


class SillyRead(SillyUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Silly readout"
    CONFIGURATION_CLASS = SillyConfiguration
    CONFIGURATION_FILE_PATH = SILLY_APP_CONFIG / "silly_read.cfg"

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Dumb data processing routine---print out the actual event.
        """
        packet = SillyPacket.unpack(packet_data)
        logger.debug(f"{packet} <- {packet_data}")
        return packet


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(SillyMainWindow, SillyRunControl(), SillyRead())


if __name__ == "__main__":
    main()
