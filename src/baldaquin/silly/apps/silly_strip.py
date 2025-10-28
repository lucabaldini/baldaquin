# Copyright (C) 2025 the baldaquin team.
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

"""Silly application with strip charts.
"""

from aptapy.plotting import VerticalCursor
from aptapy.strip import StripChart

from baldaquin import silly
from baldaquin.__qt__ import QtWidgets
from baldaquin.gui import bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket, PacketFile
from baldaquin.runctrl import RunControlBase
from baldaquin.silly.common import (
    SillyConfiguration,
    SillyMainWindow,
    SillyPacket,
    SillyRunControl,
    SillyUserApplicationBase,
)


class MainWindow(SillyMainWindow):

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.hide_reset_button()
        self.strip_tab = self.add_plot_canvas_tab("Strip charts")
        self.tab_widget.setCurrentWidget(self.strip_tab)

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        # This line is ugly, and we should find a better way to provide the user
        # application with access to the axes objects in the plotting widgets.
        user_application.axes = self.strip_tab.axes
        self.strip_tab.register(user_application.strip_chart)


class SillyStripConfiguration(SillyConfiguration):

    """Configuration class for the silly strip chart application.

    We basically extend the silly configuration with a parameter describing the
    maximum length of the strip chart.
    """

    _PARAMETER_SPECS = SillyConfiguration._PARAMETER_SPECS + \
        (("strip_chart_max_length", int, 100, "Strip chart maximum length",
          dict(min=10, max=1000000)),)


class SillyStrip(SillyUserApplicationBase):

    """Simple user application for testing purposes.
    """

    NAME = "Silly strip chart display"
    CONFIGURATION_CLASS = SillyStripConfiguration
    CONFIGURATION_FILE_PATH = silly.SILLY_APP_CONFIG / "silly_strip.cfg"

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()
        self.strip_chart = StripChart(label="Random data", xlabel="Trigger ID", ylabel="PHA")
        self.axes = None
        self._cursor = None

    def configure(self) -> None:
        """Overloaded method.
        """
        max_length = self.configuration.application_section().value("strip_chart_max_length")
        self.strip_chart.set_max_length(max_length)

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Dumb data processing routine---print out the actual event.
        """
        packet = SillyPacket.unpack(packet_data)
        self.strip_chart.put(packet.trigger_id, packet.pha)
        return packet

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        if self._cursor is not None:
            self._cursor.deactivate()
            self._cursor = None

    def post_stop(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        Also, it would be nice to understand exactly why we need to clear the axis and
        re-plot the strip chart for the cursor to pick the right color. In my mind
        the last_line_color() should do this behind the scenes, but clearly it does not.
        """
        logger.debug("Clearing strip charts...")
        # First thing first, set to None the maximum length for all the strip charts
        # to allow unlimited deque size. (Note this creates two new deques under the
        # hood, so we don't need to clear the strip charts explicitly. Also note
        # that the proper maximum length will be re-applied in the configure() slot,
        # based on the value from the GUI.)
        self.strip_chart.set_max_length(None)
        # Read all the data from disk and rebuild the entire strip charts.
        logger.debug("Re-reading all run data from disk...")
        with PacketFile(SillyPacket).open(run_control.data_file_path()) as input_file:
            for packet in input_file:
                self.strip_chart.put(packet.trigger_id, packet.pha)
        # Plot the strip charts and activate the vertical cursor.
        self.axes.clear()
        self._cursor = VerticalCursor(self.axes)
        self.strip_chart.plot(self.axes)
        self._cursor.add_marker(self.strip_chart.spline())
        self.axes.figure.canvas.draw()
        self._cursor.activate()


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(MainWindow, SillyRunControl(), SillyStrip())


if __name__ == "__main__":
    main()
