# Copyright (C) 2022--2024 the baldaquin team.
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

"""Silly application with Histogram display.
"""

import numpy as np
from aptapy.hist import Histogram1d

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
        self.pha_tab = self.add_plot_canvas_tab("PHA distribution")

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.pha_tab.register(user_application.pha_hist)


class SillyHist(SillyUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Silly histogram display"
    CONFIGURATION_CLASS = SillyConfiguration
    CONFIGURATION_FILE_PATH = silly.SILLY_APP_CONFIG / "silly_hist.cfg"

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()
        self.pha_hist = Histogram1d(np.linspace(800., 1200., 100), xlabel="PHA [ADC counts]")

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Dumb data processing routine---print out the actual event.
        """
        packet = SillyPacket.unpack(packet_data)
        self.pha_hist.fill(packet.pha)
        return packet


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(MainWindow, SillyRunControl(), SillyHist())


if __name__ == "__main__":
    main()
