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

"""Simplest possible mock application.
"""

from loguru import logger

from baldaquin.gui import bootstrap_window
from baldaquin.silly import SILLY_APP_CONFIG
from baldaquin.silly.silly import SillyRunControl, SillyPacket, SillyServer,\
    SillyUserApplicationBase, SillyConfiguration, SillyMainWindow




class UserApplication(SillyUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Simplest readout'
    CONFIGURATION_CLASS = SillyConfiguration
    CONFIGURATION_FILE_PATH = SILLY_APP_CONFIG / 'simplest_readout.cfg'

    def process_packet(self, payload):
        """Dumb data processing routine---print out the actual event.
        """
        packet = SillyPacket.unpack(payload)
        logger.debug(f'{packet} <- {payload}')



if __name__ == '__main__':
    bootstrap_window(SillyMainWindow, SillyRunControl(), UserApplication())
