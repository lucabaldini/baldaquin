# Copyright (C) 2024--25 the baldaquin team.
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

from pathlib import Path

from baldaquin import plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.buf import WriteMode
from baldaquin.egu import ThermistorConversion
from baldaquin.gui import MainWindow, SimpleControlBar, bootstrap_window
from baldaquin.pkt import AbstractPacket, packetclass
from baldaquin.plasduino import PLASDUINO_APP_CONFIG, PLASDUINO_SENSORS
from baldaquin.plasduino.common import (
    PlasduinoAnalogConfiguration,
    PlasduinoAnalogEventHandler,
    PlasduinoAnalogUserApplicationBase,
    PlasduinoRunControl,
)
from baldaquin.plasduino.protocol import AnalogReadout
from baldaquin.plasduino.shields import Lab1
from baldaquin.runctrl import RunControlBase


class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.strip_chart_tab = self.add_plot_canvas_tab("Strip charts")

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())


@packetclass
class TemperatureReadout(AnalogReadout):

    """Specialized class inheriting from ``AnalogReadout`` describing a temperature
    readout---this is essentially adding the conversion between ADC counts and
    temperature on top of the basic functions.

    We have decided to go this route for two reasons:

    * it makes it easy to guarantee that the conversion is performed once and
      forever when the packet object is created;
    * it allows to easily implement the text conversion.
    """

    _CONVERSION_FILE_PATH = PLASDUINO_SENSORS / "NXFT15XH103FA2B.dat"
    _ADC_NUM_BITS = 10
    _CONVERSION_COLS = (0, 2)
    _CONVERTER = ThermistorConversion.from_file(_CONVERSION_FILE_PATH, Lab1.SHUNT_RESISTANCE,
                                                _ADC_NUM_BITS, *_CONVERSION_COLS)

    OUTPUT_HEADERS = ("Pin number", "Time [s]", "Temperature [deg C]")
    OUTPUT_ATTRIBUTES = ("pin_number", "seconds", "temperature")
    OUTPUT_FMTS = ("%d", "%.3f", "%.2f")

    def __post_init__(self) -> None:
        """Post initialization.
        """
        AnalogReadout.__post_init__(self)
        self.temperature = self._CONVERTER(self.adc_value)


class TemperatureMonitor(PlasduinoAnalogUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Temperature Monitor"
    CONFIGURATION_CLASS = PlasduinoAnalogConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / "plasduino_tempmonitor.cfg"
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler
    _PINS = Lab1.TEMPMON_PINS
    _SAMPLING_INTERVAL = 500

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = self.create_strip_charts(self._PINS, ylabel="Temperature [deg C]")

    def configure(self) -> None:
        """Overloaded method.
        """
        max_length = self.configuration.application_section().value("strip_chart_max_length")
        for chart in self.strip_chart_dict.values():
            chart.set_max_length(max_length)

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        file_path = Path(f"{run_control.output_file_path_base()}_data.txt")
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, TemperatureReadout.to_text,
                                           TemperatureReadout.text_header(creator=self.NAME))

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = TemperatureReadout.unpack(packet_data)
        x, y = readout.seconds, readout.temperature
        self.strip_chart_dict[readout.pin_number].put(x, y)
        return readout


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), TemperatureMonitor())


if __name__ == "__main__":
    main()
