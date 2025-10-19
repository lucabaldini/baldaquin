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

"""Plasduino pendulum application.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from pathlib import Path

from baldaquin import plasduino
from baldaquin.buf import WriteMode
from baldaquin.env import BALDAQUIN_ENCODING
from baldaquin.gui import MainWindow, SimpleControlBar, bootstrap_window
from baldaquin.logging_ import logger
from baldaquin.pkt import AbstractPacket, Edge, PacketFile
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.common import (
    PlasduinoDigitalConfiguration,
    PlasduinoDigitalEventHandler,
    PlasduinoDigitalUserApplicationBase,
    PlasduinoRunControl,
)
from baldaquin.plasduino.protocol import COMMENT_PREFIX, TEXT_SEPARATOR, DigitalTransition
from baldaquin.runctrl import RunControlBase


class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar


@dataclass
class Oscillation:

    """Small convenience class to represent post-processed data.
    """

    average_time: float
    period: float
    transit_time: float

    @staticmethod
    def text_header(prefix: str = COMMENT_PREFIX, creator: str = None) -> str:
        """Text header for the post-processed output file.
        """
        return f"{AbstractPacket.text_header(prefix, creator)}" \
               f"{prefix}Time [s], Period [s], Transit time [s]\n"

    def to_text(self, separator: str = TEXT_SEPARATOR) -> str:
        """Text representation for the output file.
        """
        return f"{self.average_time:.6f}{separator}{self.period:.6f}" \
               f"{separator}{self.transit_time:.6f}\n"


class Pendulum(PlasduinoDigitalUserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = "Pendulum"
    CONFIGURATION_CLASS = PlasduinoDigitalConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / "plasduino_pendulum.cfg"
    EVENT_HANDLER_CLASS = PlasduinoDigitalEventHandler

    def pre_start(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        Here we are simply adding a text sink to the underlying data buffer to
        write the packets in text form.
        """
        file_path = Path(f"{run_control.output_file_path_base()}_data.txt")
        self.event_handler.add_custom_sink(file_path, WriteMode.TEXT, DigitalTransition.to_text,
                                           DigitalTransition.text_header(creator=self.NAME))

    @staticmethod
    def _secs_avg(data: tuple[DigitalTransition], i: int, j: int) -> float:
        """Convenience function for calculating the average value of the `seconds`
        fields for two given indices in a tuple of digital transitions.

        This is used in the post-processing functions, and it is meant to reduce
        boilerplate code and improve readability.
        """
        return 0.5 * (data[i].seconds + data[j].seconds)

    @staticmethod
    def _secs_diff(data: tuple[DigitalTransition], i: int, j: int) -> float:
        """Convenience function for calculating the difference of the `seconds`
        fields for two given indices in a tuple of digital transitions.

        This is used in the post-processing functions, and it is meant to reduce
        boilerplate code and improve readability.
        """
        return data[i].seconds - data[j].seconds

    @staticmethod
    def _postprocess_data_simple(data: tuple[DigitalTransition]) -> list[Oscillation]:
        """Simple data postprocessing.

        We do not attempt any average for the transit time and, therefore, expect
        to observe small "jumps" up and down if the optical gate is not aligned with the
        pendulum.
        """
        logger.info(f"Running Pendulum.{inspect.currentframe().f_code.co_name}()...")
        oscillations = []
        for i in range(3, len(data) - 1, 2):
            average_time = Pendulum._secs_avg(data, i, i - 1)
            transit_time = Pendulum._secs_diff(data, i, i - 1)
            period = Pendulum._secs_diff(data, i + 1, i - 3)
            oscillations.append(Oscillation(average_time, period, transit_time))
        return oscillations

    @staticmethod
    def _postprocess_data_smooth(data: tuple[DigitalTransition]) -> list[Oscillation]:
        """Slightly more advanced data postprocessing, with a little bit of averaging.
        """
        logger.info(f"Running Pendulum.{inspect.currentframe().f_code.co_name}()...")
        oscillations = []
        for i in range(5, len(data) - 3, 2):
            t1 = Pendulum._secs_avg(data, i - 4, i - 5)
            t2 = Pendulum._secs_avg(data, i - 2, i - 3)
            t3 = Pendulum._secs_avg(data, i, i - 1)
            t4 = Pendulum._secs_avg(data, i + 2, i + 1)
            dt2 = Pendulum._secs_diff(data, i - 2, i - 3)
            dt3 = Pendulum._secs_diff(data, i, i - 1)
            average_time = 0.5 * (t2 + t3)
            transit_time = 0.5 * (dt2 + dt3)
            period = 0.5 * (t3 - t1 + t4 - t2)
            oscillations.append(Oscillation(average_time, period, transit_time))
        return oscillations

    @staticmethod
    def postprocess_data(data: tuple[DigitalTransition]):
        """Postprocess the pendulum raw data in order to calculate the period and
        the transit time for all the oscillations.

        Mind we skip the first edge if the polarity is wrong---i.e. the
        data acquisition is started with the flag covering the optical gate.
        """
        # Note when Edge is an IntEnum we can get rid of the value, here.
        if data[0].edge == Edge.RISING:
            logger.info("Wrong edge detected on the first transition, skipping it...")
            data = data[1:]
        return Pendulum._postprocess_data_smooth(data)

    def post_stop(self, run_control: RunControlBase) -> None:
        """Overloaded method.

        And here we are post-processing the raw data file to calculate the actual
        high-level quantities used in the analysis.
        """
        file_path = run_control.data_file_path()
        logger.info(f"Post-processing {file_path}...")
        with PacketFile(DigitalTransition).open(file_path) as input_file:
            data = input_file.read_all()
        oscillations = self.postprocess_data(data)
        file_path = Path(f"{run_control.output_file_path_base()}_data_proc.txt")
        logger.info(f"Writing output file {file_path}...")
        with open(file_path, "w", encoding=BALDAQUIN_ENCODING) as output_file:
            output_file.write(Oscillation.text_header(creator=self.NAME))
            for oscillation in oscillations:
                output_file.write(oscillation.to_text())
        logger.info("Done.")

    def process_packet(self, packet_data: bytes) -> AbstractPacket:
        """Overloaded method.
        """
        transition = DigitalTransition.unpack(packet_data)
        return transition


def main() -> None:
    """Main entry point.
    """
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), Pendulum())


if __name__ == "__main__":
    main()
