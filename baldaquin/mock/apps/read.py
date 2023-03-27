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

import sys

from loguru import logger

from baldaquin.gui import bootstrap_window
from baldaquin.mock import MOCK_APP_CONFIG
from baldaquin.mock.mock import MockRunControl, MockMainWindow, MockEvent,\
    MockUserApplicationBase, MockEventServerConfiguration


class Configuration(MockEventServerConfiguration):

    """User application configuration.
    """



class UserApplication(MockUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Simplest readout'
    CONFIGURATION_CLASS = Configuration
    CONFIGURATION_FILE_PATH = MOCK_APP_CONFIG / 'simplest_readout.cfg'

    def configure(self):
        """Overloaded method.
        """
        #pylint: disable=useless-super-delegation
        super().configure()

    def process_event_data(self, event_data):
        """Dumb data processing routine---print out the actual event.
        """
        event = MockEvent.unpack(event_data)
        logger.debug(f'{event} <- {event_data}')



if __name__ == '__main__':
    qapp, window = bootstrap_window(MockMainWindow)
    run_control = MockRunControl()
    window.connect_to_run_control(run_control)
    run_control.load_user_application(UserApplication())
    window.show()
    sys.exit(qapp.exec())
