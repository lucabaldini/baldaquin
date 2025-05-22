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

"""xnucleo common resources.
"""

import datetime
import time

from baldaquin import logger
from baldaquin import arduino_
from baldaquin import xnucleo
from baldaquin.app import UserApplicationBase
from baldaquin.arduino_ import ArduinoSerialInterface
from baldaquin.event import EventHandlerBase
from baldaquin.runctrl import RunControlBase
from baldaquin.timeline import Timeline


# List of supported boards, i.e., only the arduino uno at the moment.
_SUPPORTED_BOARDS = (arduino_.UNO, )


class XnucleoSerialInterface(ArduinoSerialInterface):

    """Specialized xnucleo serial interface.

    This is derived class of our basic serial interface, where we essentially
    implement the simple plasduino communication protocol.
    """

    def write_readout_command(self) -> None:
        """Write the readout command to the serial port.
        """
        self.pack_and_write(1, 'B')


class XnucleoRunControl(RunControlBase):

    """Specialized xnucleo run control.
    """

    _PROJECT_NAME = xnucleo.PROJECT_NAME


class XnucleoEventHandler(EventHandlerBase):

    """Base class for all the xnucleo event handlers.
    """

    _DEFAULT_SAMPLING_INTERVAL = 1.0

    def __init__(self) -> None:
        """Constructor.

        Note we create an empty serial interface, here, and we then open the port
        while setting up the user application.
        """
        super().__init__()
        self.serial_interface = XnucleoSerialInterface()
        self.timeline = Timeline()
        self._sampling_interval = self._DEFAULT_SAMPLING_INTERVAL

    def set_sampling_interval(self, interval: float) -> None:
        """Set the sampling interval.
        """
        logger.info(f'Setting {self.__class__.__name__} sampling interval to {interval} s...')
        self._sampling_interval = interval

    def open_serial_interface(self, timeout: float = None) -> None:
        """Open the serial interface.

        ..warning::
            Note pylint is signaling a code duplication with baldaquin.plasduino.common:[241:246]
            which means that we probably need some refactoring here.
        """
        port_info = arduino_.autodetect_arduino_board(*_SUPPORTED_BOARDS)
        if port_info is None:
            raise RuntimeError('Could not find a suitable arduino board connected.')
        self.serial_interface.connect(port_info, timeout=timeout)
        self.serial_interface.pulse_dtr()

    def close_serial_interface(self) -> None:
        """Close the serial interface.
        """
        self.serial_interface.disconnect()

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
        self.serial_interface.write_readout_command()
        # Latch the timestamp (seconds since the epoch, UTC) on the host PC.
        timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()
        # Wait...
        time.sleep(self._sampling_interval)
        # Read the data from the serial port...
        data = self.serial_interface.read_text_line()
        # ... and prepend the timestamp.
        data.prepend(f'{timestamp:.3f}')
        return data


class XnucleoUserApplicationBase(UserApplicationBase):

    """Base class for all the xnucleo applications.
    """

    def configure(self) -> None:
        """Overloaded method.
        """

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()
        # FIXME
        self.event_handler.serial_interface.handshake('xnucleo_monitor', 3,
                                                      xnucleo.XNUCLEO_SKETCHES)

    def teardown(self) -> None:
        """Overloaded method (STOPPED -> RESET).
        """
        self.event_handler.close_serial_interface()
