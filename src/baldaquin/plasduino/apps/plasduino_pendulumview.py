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

"""Plasduino pendulum viewer application.
"""

from pathlib import Path

from aptapy.plotting import VerticalCursor

from baldaquin import plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.buf import WriteMode
from baldaquin.gui import MainWindow, SimpleControlBar, bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket, PacketFile, packetclass
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
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
        self.strip_chart_tab = self.add_plot_canvas_tab("Strip charts", update_interval=100)
        self.tab_widget.setCurrentWidget(self.strip_chart_tab)

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        # This line is ugly, and we should find a better way to provide the user
        # application with access to the axes objects in the plotting widgets.
        user_application.axes = self.strip_chart_tab.axes
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())


@packetclass
class PositionReadout(AnalogReadout):

    """Specialized class inheriting from ``AnalogReadout`` describing a position
    readout---this is just changing the label for the text otuput.
    """

    OUTPUT_HEADERS = ("Pin number", "Time [s]", "Position [a. u.]")


class PendulumView(PlasduinoAnalogUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Pendulum View"
    CONFIGURATION_CLASS = PlasduinoAnalogConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / "plasduino_pendulumview.cfg"
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler
    _PINS = Lab1.PENDVIEW_PINS
    _SAMPLING_INTERVAL = 50

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = self.create_strip_charts(self._PINS, ylabel="Position [ADC counts]")
        self.axes = None
        self._cursor = None

    def configure(self) -> None:
        """Overloaded method.
        """
        max_length = self.configuration.application_section().value("strip_chart_max_length")
        for chart in self.strip_chart_dict.values():
            chart.set_max_length(max_length)

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = PositionReadout.unpack(packet_data)
        self.strip_chart_dict[readout.pin_number].put(readout.seconds, readout.adc_value)
        return readout

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        # If we are starting a run after the completion of a previous one, deactivate
        # the previous interactive cursor and delete the corresponding reference.
        if self._cursor is not None:
            self._cursor.deactivate()
            self._cursor = None
        # And create the sink for the output text file.
        file_path = Path(f"{run_control.output_file_path_base()}_data.txt")
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, PositionReadout.to_text,
                                           PositionReadout.text_header(creator=self.NAME))

    def post_stop(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        This is where we re-read all the data from disk to populate the complete
        strip charts, and then enable the vertical cursor.
        """
        logger.debug("Clearing strip charts...")
        # First thing first, set to None the maximum length for all the strip charts
        # to allow unlimited deque size. (Note this creates two new deques under the
        # hood, so we don't need to clear the strip charts explicitly. Also note
        # that the proper maximum length will be re-applied in the configure() slot,
        # based on the value from the GUI.)
        for chart in self.strip_chart_dict.values():
            chart.set_max_length(None)
        # Read all the data from disk and rebuild the entire strip charts.
        logger.debug("Re-reading all run data from disk...")
        with PacketFile(PositionReadout).open(run_control.data_file_path()) as input_file:
            for readout in input_file:
                self.strip_chart_dict[readout.pin_number].put(readout.seconds, readout.adc_value)
        # Plot the strip charts and activate the vertical cursor.
        logger.debug("Activating vertical cursor on strip charts...")
        self.axes.clear()
        self._cursor = VerticalCursor(self.axes)
        for chart in self.strip_chart_dict.values():
            chart.plot(self.axes)
            self._cursor.add_marker(chart.spline())
        self.axes.figure.canvas.draw()
        self._cursor.activate()


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), PendulumView())


if __name__ == "__main__":
    main()
