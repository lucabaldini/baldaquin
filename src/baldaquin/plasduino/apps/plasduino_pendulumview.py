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

from baldaquin.buf import WriteMode
from baldaquin.env import BALDAQUIN_ENCODING
from baldaquin.gui import bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket, PacketFile, packetclass
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
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

    _UPDATE_INTERVAL = 100


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
    _LABEL = "Position [ADC counts]"
    _SAMPLING_INTERVAL = 50

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        readout = PositionReadout.unpack(packet_data)
        self.strip_chart_dict[readout.pin_number].put(readout.seconds, readout.adc_value)
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
            fields += [f"Time{pin}", f"ADC{pin}"]
        header = f"{header}# {delimiter.join(fields)}\n"
        with PacketFile(PositionReadout).open(file_path) as input_file, \
             open(output_file_path, "w", encoding=BALDAQUIN_ENCODING) as output_file:
            row = []
            output_file.write(header)
            for readout in input_file:
                row += [f"{readout.seconds:.3f}", f"{ readout.adc_value}"]
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
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, PositionReadout.to_text,
                                           PositionReadout.text_header(creator=self.NAME))

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
        with PacketFile(PositionReadout).open(run_control.data_file_path()) as input_file:
            for readout in input_file:
                self.strip_chart_dict[readout.pin_number].put(readout.seconds, readout.adc_value)
        # Plot the strip charts and activate the vertical cursor.
        self.activate_cursors()


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), PendulumView())


if __name__ == "__main__":
    main()
