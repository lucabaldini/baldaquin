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


import datetime
import time
from dataclasses import dataclass
from pathlib import Path

from aptapy.strip import EpochStripChart

from baldaquin import xnucleo
from baldaquin.__qt__ import QtWidgets
from baldaquin.app import UserApplicationBase
from baldaquin.arduino_ import ArduinoEventHandler
from baldaquin.buf import WriteMode
from baldaquin.config import UserApplicationConfiguration
from baldaquin.gui import MainWindow, SimpleControlBar, bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket
from baldaquin.runctrl import RunControlBase


@dataclass
class MonitorReadout(AbstractPacket):

    """Class describing a full readout for the xnucleo monitor application.
    """

    seconds: float
    humidity: float
    temperature1: float
    pressure: float
    temperature2: float
    adc1: int
    adc2: int
    _data: bytes = None

    OUTPUT_HEADERS = ("Time [s]", "Temperature 1 [deg C]", "Temperature 2 [deg C]",
                      "Relative humidity [%]", "Pressure [mbar]",
                      "Channel 1 [ADC counts]", "Channel 2 [ADC counts]")
    OUTPUT_ATTRIBUTES = ("seconds", "temperature1", "temperature2", "humidity",
                         "pressure", "adc1", "adc2")
    OUTPUT_FMTS = ("%.3f", "%.2f", "%.2f", "%.2f", "%.2f", "%d", "%d")

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
        fields = data.unpack(float, float, float, float, float, int, int)
        return cls(*fields, data)

    @classmethod
    def text_header(cls, prefix: str = "#", creator: str = None) -> str:
        """Return the text header.
        """
        headers = ", ".join(map(str, cls.OUTPUT_HEADERS))
        return f"{AbstractPacket.text_header(prefix, creator)}{prefix}{headers}\n"

    def to_text(self, separator: str = ",") -> str:
        """Overloaded method.
        """
        return self._text(self.OUTPUT_ATTRIBUTES, self.OUTPUT_FMTS, separator)


class MonitorWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = xnucleo.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.hide_reset_button()
        self.temperature_tab = self.add_plot_canvas_tab("Temperature")
        self.humidity_tab = self.add_plot_canvas_tab("Humidity")
        self.pressure_tab = self.add_plot_canvas_tab("Pressure")
        self.analog_tab = self.add_plot_canvas_tab("Analog inputs")

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


class MonitorConfiguration(UserApplicationConfiguration):

    _PARAMETER_SPECS = (
        ("sampling_interval", float, 2., "Sampling interval [s]",
            dict(min=1., max=1000.0)),
        ("strip_chart_max_length", int, 200, "Strip chart maximum length",
            dict(min=10, max=1000000)),
    )


class MonitorEventHandler(ArduinoEventHandler):

    """Base class for all the xnucleo event handlers.
    """

    _DEFAULT_SAMPLING_INTERVAL = 1.0

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        self._sampling_interval = self._DEFAULT_SAMPLING_INTERVAL

    def set_sampling_interval(self, interval: float) -> None:
        """Set the sampling interval.
        """
        logger.info(f"Setting {self.__class__.__name__} sampling interval to {interval} s...")
        self._sampling_interval = interval

    def read_packet(self) -> bytes:
        """Basic function fetching a single readout from the xnucleo board attached
        to the arduino.

        This looks somewhat more convoluted than it might be for the simple reason
        that we are trying to stick to the basic baldaquin protocol, where data
        are fetched from the board interfaced to the host PC, and the latter is just
        waiting. Here, instead, we are sending arduino a byte on the serial port
        to trigger a readout, we are latching the timestamp on the host PC, we are
        reading the data from the serial port, and we are assembling everything
        together in a single bytes object that is then written to disk in binary format.
        """
        # Trigger a readout on the arduino board.
        self.serial_interface.pack_and_write(1, "B")
        # Latch the timestamp (seconds since the epoch, UTC) on the host PC.
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        # Wait...
        time.sleep(self._sampling_interval)
        # Read the data from the serial port...
        data = self.serial_interface.read_text_line()
        # ... and prepend the timestamp.
        data.prepend(f"{timestamp:.3f}")
        return data


class MonitorRunControl(RunControlBase):

    """Specialized xnucleo run control.
    """

    _PROJECT_NAME = xnucleo.PROJECT_NAME


class Monitor(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Generic Monitor"
    CONFIGURATION_CLASS = MonitorConfiguration
    CONFIGURATION_FILE_PATH = xnucleo.XNUCLEO_APP_CONFIG / "xnucleo_monitor.cfg"
    EVENT_HANDLER_CLASS = MonitorEventHandler
    SKETCH_NAME = "xnucleo_monitor"
    SKETCH_VERSION = 3

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        kwargs = dict(ylabel="Temperature [deg C]")
        self.temperature1_strip_chart = EpochStripChart(label="Temperature 1", **kwargs)
        self.temperature2_strip_chart = EpochStripChart(label="Temperature 2", **kwargs)
        kwargs = dict(ylabel="Humidity [%]")
        self.humidity_strip_chart = EpochStripChart(**kwargs)
        kwargs = dict(ylabel="Pressure [mbar]")
        self.pressure_strip_chart = EpochStripChart(**kwargs)
        kwargs = dict(ylabel="Value [ADC counts]")
        self.adc1_strip_chart = EpochStripChart(label="Channel 1", **kwargs)
        self.adc2_strip_chart = EpochStripChart(label="Channel 2", **kwargs)
        self._strip_charts = (self.temperature1_strip_chart, self.temperature2_strip_chart,
                              self.humidity_strip_chart, self.pressure_strip_chart,
                              self.adc1_strip_chart, self.adc2_strip_chart)

    def configure(self) -> None:
        """Overloaded method.
        """
        config = self.configuration.application_section()
        self.event_handler.set_sampling_interval(config.value("sampling_interval"))
        for chart in self._strip_charts:
            chart.set_max_length(config.value("strip_chart_max_length"))

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()
        args = self.SKETCH_NAME, self.SKETCH_VERSION, xnucleo.XNUCLEO_SKETCHES
        self.event_handler.serial_interface.handshake(*args)

    def teardown(self) -> None:
        """Overloaded method (STOPPED -> RESET).
        """
        self.event_handler.close_serial_interface()

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        file_path = Path(f"{run_control.output_file_path_base()}_data.txt")
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, MonitorReadout.to_text,
                                           MonitorReadout.text_header(creator=self.NAME))

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = MonitorReadout.unpack(packet_data)
        seconds = readout.seconds
        self.temperature1_strip_chart.put(seconds, readout.temperature1)
        self.temperature2_strip_chart.put(seconds, readout.temperature2)
        self.humidity_strip_chart.put(seconds, readout.humidity)
        self.pressure_strip_chart.put(seconds, readout.pressure)
        self.adc1_strip_chart.put(seconds, readout.adc1)
        self.adc2_strip_chart.put(seconds, readout.adc2)
        return readout


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(MonitorWindow, MonitorRunControl(), Monitor())


if __name__ == "__main__":
    main()
