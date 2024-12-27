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
from baldaquin import logger
from baldaquin.__qt__ import QtWidgets
from baldaquin.egu import ThermistorConversion
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.plasduino import PLASDUINO_APP_CONFIG, PLASDUINO_SENSORS
from baldaquin.plasduino.plasduino import PlasduinoRunControl, PlasduinoAnalogEventHandler,\
    PlasduinoAnalogConfiguration, PlasduinoAnalogUserApplicationBase
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
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())



class TemperatureMonitor(PlasduinoAnalogUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Temperature Monitor'
    CONFIGURATION_CLASS = PlasduinoAnalogConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'temperature_monitor.cfg'
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler
    _SAMPLING_INTERVAL = 500
    _CONVERSION_FILE_PATH = PLASDUINO_SENSORS / 'NXFT15XH103FA2B.dat'
    _CONVERSION_COLS = (0, 2)

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = self.create_strip_charts(ylabel='Temperature [deg C]')
        args = self._CONVERSION_FILE_PATH, Lab1.SHUNT_RESISTANCE, 10, *self._CONVERSION_COLS
        self._converter = ThermistorConversion.from_file(*args)

    def configure(self):
        """Overloaded method.
        """
        for chart in self.strip_chart_dict.values():
            chart.reset(self.configuration.value('strip_chart_max_length'))

    def process_packet(self, packet) -> None:
        """Overloaded method.
        """
        readout = AnalogReadout.unpack(packet)
        self.strip_chart_dict[readout.pin_number].add_point(readout.timestamp,
            self._converter(readout.adc_value))



if __name__ == '__main__':
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), TemperatureMonitor())
