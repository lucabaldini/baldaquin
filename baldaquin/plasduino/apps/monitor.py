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

"""Plasduino monitor application.
"""

import numpy as np

from baldaquin.__qt__ import QtWidgets
from baldaquin.app import UserApplicationBase
from baldaquin.config import ConfigurationBase
from baldaquin.event import EventHandlerBase
from baldaquin.gui import bootstrap_window
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.plasduino import PlasduinoMainWindow, PlasduinoRunControl
from baldaquin.plasduino.protocol import PlasduinoSerialInterface



class MainWindow(PlasduinoMainWindow):

    """
    """

    # def __init__(self, parent : QtWidgets.QWidget = None) -> None:
    #     """Constructor.
    #     """
    #     super().__init__()
    #     self.pha_tab = self.add_plot_canvas_tab('PHA distribution')
    #
    # def setup_user_application(self, user_application):
    #     """Overloaded method.
    #     """
    #     super().setup_user_application(user_application)
    #     plot_pha_hist = lambda : self.pha_tab.draw_histogram(user_application.pha_hist)
    #     plot_pha_hist()
    #     self.pha_tab.connect_slot(plot_pha_hist)



class Configuration(ConfigurationBase):

    """User application configuration.
    """


class EventHandler(EventHandlerBase):

    """Mock event handler for testing purpose.
    """

    #BUFFER_CLASS = CircularBuffer
    #BUFFER_KWARGS = dict(max_size=20, flush_size=10, flush_interval=2.)

    def read_event_data(self):
        """Read a single event.
        """
        print('Reading...')


class UserApplication(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Temperature monitor'
    CONFIGURATION_CLASS = Configuration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'monitor.cfg'
    EVENT_HANDLER_CLASS = EventHandler

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()

    def configure(self):
        """Overloaded method.
        """
        

    def process_event_data(self, event_data):
        """Dumb data processing routine---print out the actual event.
        """
        #event = MockEvent.unpack(event_data)
        #self.pha_hist.fill(event.pha)



if __name__ == '__main__':
    bootstrap_window(MainWindow, PlasduinoRunControl(), UserApplication())
