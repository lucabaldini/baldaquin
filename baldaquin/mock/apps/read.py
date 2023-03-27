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

from baldaquin.app import UserApplicationBase
from baldaquin.config import ConfigurationBase
from baldaquin.gui import bootstrap_window
from baldaquin.mock import MOCK_APP_CONFIG
from baldaquin.mock.mock import MockRunControl, MockMainWindow, MockEventHandler


class Configuration(ConfigurationBase):

    """Configuration structure for the mock uaser app.
    """

    TITLE = 'Configuration'
    PARAMETER_SPECS = (
        ('rate', 'float', 5., 'Target event rate', 'Hz', '.1f', dict(min=0.)),
        ('pha_mean', 'float', 1000., 'Mean pulse height', 'ADC counts', '.1f', dict(min=500., max=10000.)),
        ('pha_sigma', 'float', 50., 'Pulse height rms', 'ADC counts', '.1f', dict(min=10.))
    )


class UserApplication(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Simplest readout'
    EVENT_HANDLER_CLASS = MockEventHandler
    CONFIGURATION_CLASS = Configuration
    CONFIGURATION_FILE_PATH = MOCK_APP_CONFIG / 'simplest_readout.cfg'

    def configure(self):
        """Overloaded method.
        """
        rate = self.configuration.value('rate')
        pha_mean = self.configuration.value('pha_mean')
        pha_sigma = self.configuration.value('pha_sigma')
        self.event_handler.setup_server(rate, pha_mean, pha_sigma)

    def process_event_data(self):
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
