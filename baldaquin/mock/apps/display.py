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

"""Mock application with data display.
"""

import numpy as np

from baldaquin.__qt__ import QtWidgets
from baldaquin.gui import bootstrap_window
from baldaquin.hist import Histogram1d
from baldaquin.mock import MOCK_APP_CONFIG, MOCK_PROJECT_NAME
from baldaquin.mock.mock import MockRunControl, MockMainWindow, MockEvent,\
    MockUserApplicationBase, MockEventServerConfiguration



class MainWindow(MockMainWindow):

    """Mock main window for testing purposes.
    """

    PROJECT_NAME = MOCK_PROJECT_NAME
    # pylint: disable=c-extension-no-member

    def __init__(self, parent : QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.pha_tab = self.add_plot_canvas_tab('PHA distribution')

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        plot_pha_hist = lambda : self.pha_tab.draw_histogram(user_application.pha_hist)
        plot_pha_hist()
        self.pha_tab.connect_slot(plot_pha_hist)



class Configuration(MockEventServerConfiguration):

    """User application configuration.
    """



class UserApplication(MockUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Readout and display'
    CONFIGURATION_CLASS = Configuration
    CONFIGURATION_FILE_PATH = MOCK_APP_CONFIG / 'display.cfg'

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()
        self.pha_hist = Histogram1d(np.linspace(800., 1200., 100), xlabel='PHA [ADC counts]')

    def configure(self):
        """Overloaded method.
        """
        #pylint: disable=useless-super-delegation
        super().configure()

    def process_event_data(self, event_data):
        """Dumb data processing routine---print out the actual event.
        """
        event = MockEvent.unpack(event_data)
        self.pha_hist.fill(event.pha)



if __name__ == '__main__':
    bootstrap_window(MainWindow, MockRunControl(), UserApplication())
