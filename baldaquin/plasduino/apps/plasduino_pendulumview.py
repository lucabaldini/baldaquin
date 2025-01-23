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

"""Plasduino pendulum viewer application.
"""

from pathlib import Path

from baldaquin import plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.buf import WriteMode
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.pkt import AbstractPacket
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.common import PlasduinoRunControl, PlasduinoAnalogEventHandler, \
    PlasduinoAnalogConfiguration, PlasduinoAnalogUserApplicationBase
from baldaquin.plasduino.protocol import COMMENT_PREFIX, TEXT_SEPARATOR, AnalogReadout


class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.strip_chart_tab = self.add_plot_canvas_tab('Strip charts', update_interval=100)

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())


class PendulumView(PlasduinoAnalogUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Pendulum View'
    CONFIGURATION_CLASS = PlasduinoAnalogConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'plasduino_pendulumview.cfg'
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler
    _SAMPLING_INTERVAL = 100

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = self.create_strip_charts(ylabel='Position [ADC counts]')

    @staticmethod
    def text_header() -> str:
        """Return the header for the output text file.
        """
        return f'{AbstractPacket.text_header()}\n' \
               f'{COMMENT_PREFIX}Pin number{TEXT_SEPARATOR}Time [s]' \
               f'{TEXT_SEPARATOR}Position [ADC counts]\n'

    def readout_to_text(self, readout: AnalogReadout) -> str:
        """Convert a temperature readout to text for use in a custom sink.
        """
        return f'{readout.pin_number}{TEXT_SEPARATOR}{readout.seconds:.3f}' \
               f'{TEXT_SEPARATOR}{readout.adc_value}\n'

    def configure(self) -> None:
        """Overloaded method.
        """
        for chart in self.strip_chart_dict.values():
            chart.reset(self.configuration.value('strip_chart_max_length'))

    def pre_start(self) -> None:
        """Overloaded method.
        """
        file_path = Path(f'{self.current_output_file_base}_data.txt')
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, self.readout_to_text,
                                           self.text_header())

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = AnalogReadout.unpack(packet_data)
        self.strip_chart_dict[readout.pin_number].add_point(readout.seconds, readout.adc_value)
        return readout


if __name__ == '__main__':
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), PendulumView())
