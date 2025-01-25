# Copyright (C) 2024 the baldaquin team.
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

"""Plasduino pendulum application.
"""

from pathlib import Path

from baldaquin import logger
from baldaquin import plasduino
from baldaquin.buf import WriteMode
from baldaquin.gui import bootstrap_window, MainWindow, SimpleControlBar
from baldaquin.pkt import AbstractPacket, PacketFile
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.common import PlasduinoRunControl, PlasduinoDigitalEventHandler, \
    PlasduinoAnalogConfiguration, PlasduinoDigitalUserApplicationBase
from baldaquin.plasduino.protocol import COMMENT_PREFIX, TEXT_SEPARATOR, DigitalTransition
from baldaquin.runctrl import RunControlBase


class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar


class Pendulum(PlasduinoDigitalUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Pendulum'
    CONFIGURATION_CLASS = PlasduinoAnalogConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'plasduino_pendulum.cfg'
    EVENT_HANDLER_CLASS = PlasduinoDigitalEventHandler

    @staticmethod
    def text_header() -> str:
        """Return the header for the output text file.
        """
        return f'{AbstractPacket.text_header()}' \
               f'{COMMENT_PREFIX}Creator: {__file__}\n' \
               f'{COMMENT_PREFIX}Time [s]{TEXT_SEPARATOR}Edge type\n'

    def transition_to_text(self, transition: DigitalTransition) -> str:
        """Convert a temperature readout to text for use in a custom sink.
        """
        return f'{transition.seconds:.6f}{TEXT_SEPARATOR}{transition.edge}\n'

    def configure(self) -> None:
        """Overloaded method.
        """

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        Here we are simply adding a text sink to the underlying data buffer to
        write the packets in text form.
        """
        file_path = Path(f'{run_control.output_file_path_base()}_data.txt')
        args = file_path, WriteMode.TEXT, self.transition_to_text, self.text_header()
        self.event_handler.add_custom_sink(*args)

    def post_stop(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        And here we are post-processing the raw data file to calculate the actual
        high-level quantities used in the analysis.
        """
        file_path = run_control.data_file_path()
        logger.info(f'Post-processing {file_path}...')
        with PacketFile(DigitalTransition).open(file_path) as input_file:
            transitions = input_file.read_all()
        for transition in transitions:
            print(transition)

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        transition = DigitalTransition.unpack(packet_data)
        return transition


if __name__ == '__main__':
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), Pendulum())
