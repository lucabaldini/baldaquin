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

from baldaquin.buf import WriteMode
from baldaquin.egu import ThermistorConversion
from baldaquin.env import BALDAQUIN_ENCODING
from baldaquin.gui import bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket, PacketFile, packetclass
from baldaquin.plasduino import PLASDUINO_APP_CONFIG, PLASDUINO_SENSORS
from baldaquin.plasduino.common import (
    PlasduinoAnalogConfiguration,
    PlasduinoAnalogEventHandler,
    PlasduinoAnalogUserApplicationBase,
    PlasduinoMainWindow,
    PlasduinoRunControl,
)
from baldaquin.plasduino.protocol import AnalogReadout
from baldaquin.plasduino.shields import Lab1
from baldaquin.runctrl import RunControlBase


class AppMainWindow(PlasduinoMainWindow):

    pass


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
    _LABEL = "Temperature [deg C]"
    _SAMPLING_INTERVAL = 500

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = TemperatureReadout.unpack(packet_data)
        x, y = readout.seconds, readout.temperature
        self.strip_chart_dict[readout.pin_number].put(x, y)
        return readout

    @classmethod
    def post_process_file(cls, file_path: Path, delimiter: str = "   ") -> None:
        """Post-process a binary data file to produce a text output file.
        """
        logger.info(f"Post-processing file {file_path}...")
        output_file_path = file_path.with_name(file_path.stem + "_proc.txt")
        header = AbstractPacket.text_header(prefix="# ", creator=cls.NAME)
        fields = []
        for pin in cls._PINS:
            fields += [f"Time{pin}", f"Temp{pin}"]
        header = f"{header}# {delimiter.join(fields)}\n"
        with PacketFile(TemperatureReadout).open(file_path) as input_file, \
             open(output_file_path, "w", encoding=BALDAQUIN_ENCODING) as output_file:
            row = []
            output_file.write(header)
            for readout in input_file:
                row += [f"{readout.seconds:.3f}", f"{ readout.temperature:.2f}"]
                if readout.pin_number == cls._PINS[-1]:
                    output_file.write(f"{delimiter.join(row)}\n")
                    row = []
        logger.info(f"Post-processed data written to {output_file_path}")

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.
        """
        # If we are starting a run after the completion of a previous one, deactivate
        # the previous interactive cursor and delete the corresponding reference.
        self.deactivate_cursors()
        # And create the sink for the output text file.
        file_path = Path(f"{run_control.output_file_path_base()}_data.csv")
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, TemperatureReadout.to_text,
                                           TemperatureReadout.text_header(creator=self.NAME))

    def post_stop(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        This is where we re-read all the data from disk to populate the complete
        strip charts, and then enable the vertical cursor.
        """
        self.post_process_file(run_control.data_file_path())
        logger.debug("Clearing strip charts...")
        # First thing first, set to None the maximum length for all the strip charts
        # to allow unlimited deque size. (Note this creates two new deques under the
        # hood, so we don't need to clear the strip charts explicitly. Also note
        # that the proper maximum length will be re-applied in the configure() slot,
        # based on the value from the GUI.)
        for chart in self.strip_chart_dict.values():
            chart.set_max_length(None)
        # Read all the data from disk and rebuild the entire strip charts.
        logger.debug("Re-building strip charts from disk...")
        with PacketFile(TemperatureReadout).open(run_control.data_file_path()) as input_file:
            for readout in input_file:
                x, y = readout.seconds, readout.temperature
                self.strip_chart_dict[readout.pin_number].put(x, y)
        # Plot the strip charts and activate the vertical cursor.
        self.activate_cursors()


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), TemperatureMonitor())


if __name__ == "__main__":
    main()
