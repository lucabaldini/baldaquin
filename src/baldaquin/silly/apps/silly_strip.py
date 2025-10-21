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

import numpy as np
from aptapy.strip import StripChart

from baldaquin import silly
from baldaquin.__qt__ import QtWidgets
from baldaquin.gui import bootstrap_window
from baldaquin.pkt import AbstractPacket
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
        self.strip_tab = self.add_plot_canvas_tab("Strip charts")

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.strip_tab.register(user_application.strip_chart)


class SillyStrip(SillyUserApplicationBase):

    """Simple user application for testing purposes.
    """

    NAME = "Silly strip chart display"
    CONFIGURATION_CLASS = SillyConfiguration
    CONFIGURATION_FILE_PATH = silly.SILLY_APP_CONFIG / "silly_strip.cfg"

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()
        self.strip_chart = StripChart(max_length=100, label="Time series",
                                      xlabel="Trigger ID", ylabel="PHA")

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Dumb data processing routine---print out the actual event.
        """
        packet = SillyPacket.unpack(packet_data)
        self.strip_chart.put(packet.trigger_id, packet.pha)
        return packet


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(MainWindow, SillyRunControl(), SillyStrip())


if __name__ == "__main__":
    main()
