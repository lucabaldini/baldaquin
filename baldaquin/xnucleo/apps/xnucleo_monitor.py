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

"""xnucleo environmental monitor application.
"""


from pathlib import Path
import struct

from baldaquin import xnucleo
from baldaquin.__qt__ import QtWidgets
from baldaquin.buf import WriteMode
from baldaquin.config import ConfigurationBase
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.pkt import AbstractPacket
from baldaquin.runctrl import RunControlBase
from baldaquin.xnucleo.common import XnucleoRunControl, XnucleoUserApplicationBase,\
    XnucleoEventHandler


class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = xnucleo.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.strip_chart_tab = self.add_plot_canvas_tab('Strip charts')

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())


class XnucleoConfiguration(ConfigurationBase):

    """User application configuration.
    """

    PARAMETER_SPECS = ()



class MonitorReadout(AbstractPacket):

    """
    """

    def __init__(self, data: str) -> None:
        """Constructor.
        """
        self._data = data
        self.seconds = struct.unpack('d', self._data[0:8])[0]
        self.umidity, self.temperature1, self.pressure, self.temperature2 = \
            data[8:].decode().strip('#').split(';')

    @property
    def data(self) -> bytes:
        """Return the packet binary data.
        """
        return self._data

    @property
    def fields(self) -> tuple:
        """Return the packet fields.
        """

    def __len__(self) -> int:
        """Return the length of the binary data in bytes.
        """
        return len(self._data)

    def __iter__(self):
        """Iterate over the field values.
        """

    def pack(self) -> bytes:
        """Pack the field values into the corresponding binary data.
        """

    @classmethod
    def unpack(cls, data: bytes):
        """Unpack the binary data into the corresponding field values.
        """



class Monitor(XnucleoUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Generic Monitor'
    CONFIGURATION_CLASS = XnucleoConfiguration
    CONFIGURATION_FILE_PATH = xnucleo.XNUCLEO_APP_CONFIG / 'xnucleo_monitor.cfg'
    EVENT_HANDLER_CLASS = XnucleoEventHandler
    _SAMPLING_INTERVAL = 500

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        self.strip_chart_dict = {}

    def configure(self) -> None:
        """Overloaded method.
        """
        #for chart in self.strip_chart_dict.values():
        #    chart.reset(self.configuration.value('strip_chart_max_length'))

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        #file_path = Path(f'{run_control.output_file_path_base()}_data.txt')
        #self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, TemperatureReadout.to_text,
        #                                   TemperatureReadout.text_header(creator=self.NAME))

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        print(packet_data)
        readout = MonitorReadout(packet_data)
        print(readout.seconds, readout.umidity, readout.temperature1, readout.pressure, readout.temperature2)
        print(readout)
        #readout = TemperatureReadout.unpack(packet_data)
        #x, y = readout.seconds, readout.temperature
        #self.strip_chart_dict[readout.pin_number].add_point(x, y)
        return readout


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, XnucleoRunControl(), Monitor())


if __name__ == '__main__':
    main()

