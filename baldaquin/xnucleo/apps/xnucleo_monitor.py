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


from dataclasses import dataclass
from pathlib import Path
import struct

from baldaquin import xnucleo
from baldaquin.__qt__ import QtWidgets
from baldaquin.buf import WriteMode
from baldaquin.config import ConfigurationBase
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.pkt import AbstractPacket
from baldaquin.runctrl import RunControlBase
from baldaquin.strip import SlidingStripChart
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
        self.temperature_tab = self.add_plot_canvas_tab('Temperature')
        self.humidity_tab = self.add_plot_canvas_tab('Humidity')
        self.pressure_tab = self.add_plot_canvas_tab('Pressure')
        self.analog_tab = self.add_plot_canvas_tab('Analog inputs')

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        self.temperature_tab.register(user_application.temperature1_strip_chart,
                                      user_application.temperature2_strip_chart)
        self.humidity_tab.register(user_application.humidity_strip_chart)
        self.pressure_tab.register(user_application.pressure_strip_chart)
        self.analog_tab.register(user_application.adc1_strip_chart,
                                 user_application.adc2_strip_chart)


class XnucleoConfiguration(ConfigurationBase):

    """User application configuration.
    """

    PARAMETER_SPECS = ()



@dataclass
class MonitorReadout(AbstractPacket):

    """
    """

    seconds: float
    humidity: float
    temperature1: float
    pressure: float
    temperature2: float
    adc1: int
    adc2: int
    _data: bytes = None

    OUTPUT_HEADERS = ('Time [s]', 'Temperature 1 [deg C]', 'Temperature 2 [deg C]',
                      'Relative humidity [%]', 'Pressure [mbar]',
                      'Channel 1 [ADC counts]', 'Channel 2 [ADC counts]')
    OUTPUT_ATTRIBUTES = ('seconds', 'temperature1', 'temperature2', 'humidity',
                         'pressure', 'adc1', 'adc2')
    OUTPUT_FMTS = ('%.3f', '%.2f', '%.2f', '%.2f', '%.2f', '%d', '%d')

    @property
    def data(self) -> bytes:
        """Return the packet binary data.
        """
        return self._data

    @property
    def fields(self) -> tuple:
        """Return the packet fields.
        """
        return

    def __len__(self) -> int:
        """Return the length of the binary data in bytes.
        """
        return len(self._data)

    def __iter__(self):
        """Iterate over the field values.
        """
        raise NotImplementedError

    def pack(self) -> bytes:
        """Pack the field values into the corresponding binary data.
        """
        raise NotImplementedError

    @classmethod
    def unpack(cls, data: bytes):
        """Unpack the binary data into the corresponding field values.
        """
        seconds = struct.unpack('d', data[0:8])[0]
        values = [float(item) for item in data[8:].decode().strip('#').split(';')]
        return cls(seconds, *values, data)

    @classmethod
    def text_header(cls, prefix: str = '#', creator: str = None) -> str:
        """
        """
        headers = ', '.join(map(str, cls.OUTPUT_HEADERS))
        return f'{AbstractPacket.text_header(prefix, creator)}{prefix}{headers}\n'

    def to_text(self, separator: str = ',') -> str:
        """Overloaded method.
        """
        return self._text(self.OUTPUT_ATTRIBUTES, self.OUTPUT_FMTS, separator)


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
        kwargs = dict(datetime=True, ylabel='Temperature [deg C]')
        self.temperature1_strip_chart = SlidingStripChart(label='Temperature 1', **kwargs)
        self.temperature2_strip_chart = SlidingStripChart(label='Temperature 1', **kwargs)
        kwargs = dict(datetime=True, ylabel='Humidity [%]')
        self.humidity_strip_chart = SlidingStripChart(**kwargs)
        kwargs = dict(datetime=True, ylabel='Pressure [mbar]')
        self.pressure_strip_chart = SlidingStripChart(**kwargs)
        kwargs = dict(datetime=True, ylabel='Value [ADC counts]')
        self.adc1_strip_chart = SlidingStripChart(label='Channel 1', **kwargs)
        self.adc2_strip_chart = SlidingStripChart(label='Channel 2', **kwargs)

    def configure(self) -> None:
        """Overloaded method.
        """
        #for chart in self.strip_chart_dict.values():
        #    chart.reset(self.configuration.value('strip_chart_max_length'))

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        file_path = Path(f'{run_control.output_file_path_base()}_data.txt')
        print(file_path)
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, MonitorReadout.to_text,
                                           MonitorReadout.text_header(creator=self.NAME))

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = MonitorReadout.unpack(packet_data)
        seconds = readout.seconds
        self.temperature1_strip_chart.add_point(seconds, readout.temperature1)
        self.temperature2_strip_chart.add_point(seconds, readout.temperature2)
        self.humidity_strip_chart.add_point(seconds, readout.humidity)
        self.pressure_strip_chart.add_point(seconds, readout.pressure)
        self.adc1_strip_chart.add_point(seconds, readout.adc1)
        self.adc2_strip_chart.add_point(seconds, readout.adc2)
        return readout


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, XnucleoRunControl(), Monitor())


if __name__ == '__main__':
    main()
