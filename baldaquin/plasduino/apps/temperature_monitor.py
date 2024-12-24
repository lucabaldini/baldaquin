# Copyright (C) 2024 the baldaquin team.
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

"""Plasduino temperature monitor application.
"""

from baldaquin import plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.config import ConfigurationBase
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.plasduino import PlasduinoRunControl, PlasduinoAnalogEventHandler,\
    PlasduinoAnalogUserApplicationBase
from baldaquin.plasduino.protocol import AnalogReadout
from baldaquin.plasduino.shields import Lab1
from baldaquin.strip import SlidingStripChart



class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar

    def __init__(self, parent : QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.strip_chart_tab = self.add_plot_canvas_tab('Strip charts')

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        plot_strip_charts = lambda :\
            self.strip_chart_tab.draw_strip_charts(*user_application.strip_chart_dict.values())
        self.strip_chart_tab.connect_slot(plot_strip_charts)



class AppConfiguration(ConfigurationBase):

    """User application configuration.
    """

    PARAMETER_SPECS = (
        ('strip_chart_max_length', 'int', 200, 'Strip chart maximum length',
            dict(min=10, max=1000000)),
    )



class TemperatureMonitor(PlasduinoAnalogUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Temperature Monitor'
    CONFIGURATION_CLASS = AppConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'temperature_monitor.cfg'
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler
    _SAMPLING_INTERVAL = 500
    _STRIP_CHART_KWARGS = dict(xlabel='Time [s]', ylabel='ADC counts')

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = {pin: None for pin in Lab1.ANALOG_PINS}

    def _create_strip_chart(self, pin: int, max_length: int) -> SlidingStripChart:
        """Create a new strip chart for a given pin.
        """
        return SlidingStripChart(max_length, f'Pin {pin}', **self._STRIP_CHART_KWARGS)

    def configure(self):
        """Overloaded method.
        """
        max_length = self.configuration.value('strip_chart_max_length')
        self.strip_chart_dict = {pin: self._create_strip_chart(pin, max_length) \
            for pin in Lab1.ANALOG_PINS}

    def process_packet(self, packet) -> None:
        """Overloaded method.
        """
        readout = AnalogReadout.unpack(packet)
        self.strip_chart_dict[readout.pin_number].add_data_point(readout.timestamp,
            readout.adc_value)



if __name__ == '__main__':
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), TemperatureMonitor())
