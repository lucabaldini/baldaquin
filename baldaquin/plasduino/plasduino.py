# Copyright (C) 22024 the baldaquin team.
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

"""Plasduino common resources.
"""

from baldaquin import logger
from baldaquin import plasduino
from baldaquin.buf import CircularBuffer
from baldaquin.event import EventHandlerBase
from baldaquin.plasduino.protocol import PlasduinoSerialInterface
from baldaquin.runctrl import RunControlBase
from baldaquin.serial_ import list_com_ports



# List of supported boards, i.e., only the arduino uno at the moment.
# This comes in the form of a list of (vid, pid) tuples, with the numbers taken
# verbatim from https://github.com/arduino/ArduinoCore-avr/blob/master/boards.txt
# At some point we might want to do a more thorough job of listing all the
# possible (vid, pid) of the actual arduino boards with which plasduino would
# work (I am sure, e.g., that we tested the thing with arduino mega).

_SUPPORTED_BOARDS = (
    (0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x2341, 0x0243), (0x2341, 0x006A), # uno
)



def autodetect_arduino_board() -> str:
    """Autodetect a supported arduino board attached to one the serial ports, and
    return the corresponding device name (e.g., ``/dev/ttyACM0``).

    Note this returns None if no supported arduino board is found, and the the
    first board found in case there are more than one.

    Returns
    -------
    str
        The name of the (first available) port with a supported arduino attached
        to it.
    """
    ports = list_com_ports(*_SUPPORTED_BOARDS)
    if len(ports) == 0:
        return None
    if len(ports) > 1:
        logger.warning('More than one arduino board found, picking the first one...')
    return ports[0].device



class PlasduinoRunControl(RunControlBase):

    """Specialized plasduino run control.
    """

    PROJECT_NAME = plasduino.PROJECT_NAME



class PlasduinoEventHandler(EventHandlerBase):

    """Plasduino basic event handler.

    This takes care of all the operations connected with the handshaking and
    sketch upload. Derived classes must implement the ``read_packet()`` slot.
    """

    BUFFER_CLASS = CircularBuffer
    BUFFER_KWARGS = dict(max_size=1000, flush_size=100, flush_interval=5.)

    def __init__(self) -> None:
        """Constructor.

        We create an empty serial interface, here.
        """
        super().__init__()
        self.serial_interface = PlasduinoSerialInterface()

    def open_serial_interface(self) -> None:
        """Autodetect a supported arduino board, open the serial connection to it,
        and do the handshaking.

        .. warning::
            We still have to implement to sketch upload part, here.
        """
        port = autodetect_arduino_board()
        if port is None:
            raise RuntimeError('Could not find a suitable arduino board connected.')
        self.serial_interface.connect(port)
        self.serial_interface.pulse_dtr()
        logger.info('Hand-shaking with the arduino board...')
        sketch_id = self.serial_interface.read_and_unpack('B')
        sketch_version = self.serial_interface.read_and_unpack('B')
        logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')
