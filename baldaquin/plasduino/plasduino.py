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

"""Plasduino common resources.
"""

import time
from typing import Any

from baldaquin import logger
from baldaquin import plasduino
from baldaquin.buf import CircularBuffer
from baldaquin.event import EventHandlerBase
from baldaquin.plasduino.protocol import Marker, OpCode, AnalogReadout, DigitalTransition
from baldaquin.runctrl import RunControlBase
from baldaquin.serial_ import list_com_ports, SerialInterface



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
        The name of the (first available) port with a supported arduino attached to it.
    """
    ports = list_com_ports(*_SUPPORTED_BOARDS)
    if len(ports) == 0:
        return None
    if len(ports) > 1:
        logger.warning('More than one arduino board found, picking the first one...')
    return ports[0].device



class PlasduinoSerialInterface(SerialInterface):

    """Specialized plasduino serial interface.

    This is derived class of our basic serial interface, where we essentially
    implement the simple plasduino communication protocol.
    """

    # pylint: disable=too-many-ancestors

    def read_and_unpack(self, fmt: str) -> Any:
        """Overloaded function.

        For some reason on the arduino side we go into the trouble of reverting the
        native bit order and we transmit things as big endian---I have no idea
        what I was thinking, back in the days, but I don't think it makes sense
        to fix this nonsense, now. Extra work on the transmitting side, and extra
        work on the receiving side too. Good job, Luca!
        """
        return super().read_and_unpack(f'>{fmt}')

    def wait_rem(self) -> None:
        """
        """
        logger.info(f'Waiting for the run-end marker...')
        end_mark = self.read_and_unpack('B')
        if not end_mark == Marker.RUN_END_MARKER.value:
            raise RuntimeError(f'End run marker mismatch, got {hex(end_mark)}.')
        logger.info('Got it!')

    def read_until_rem(self, timeout: float = None) -> None:
        """Read data from the serial port until the end-of-run marker is found.
        """
        logger.info(f'Scanning serial input for run-end marker...')
        previous_timeout = self.timeout
        if timeout != self.timeout:
            self.timeout = timeout
            logger.debug(f'Serial port timeout temporarily set to {self.timeout} s...')
        data = self.read_until(struct.pack('B', Marker.RUN_END_MARKER.value))
        if len(data) > 0:
            logger.debug(f'{len(data)} byte(s) found: {data}')
        if previous_timeout != self.timeout:
            self.timeout = previous_timeout
            logger.debug(f'Serial port timeout restored to {self.timeout} s...')

    def write_opcode(self, opcode: OpCode) -> int:
        """Write the value of a given opcode to the serial port.

        This is typically meant to signal the start/stop run, or to configure the
        behavior of the sketch on the arduino side (e.g., select the pins for
        analog readout).
        """
        logger.debug(f'Writing {opcode} to the serial port...')
        return self.pack_and_write(opcode.value, 'B')

    def write_start_run(self) -> int:
        """ Write a start run command to the serial port.
        """
        return self.write_opcode(OpCode.OP_CODE_START_RUN)

    def write_stop_run(self) -> int:
        """ Write a stop run command to the serial port.
        """
        return self.write_opcode(OpCode.OP_CODE_STOP_RUN)

    def write_cmd(self, opcode: OpCode, value: int, fmt: str) -> None:
        """ Write a command to the arduino board.

        This implies writing the opcode to the serial port, writing the actual
        payload and, finally, reading back the arduino response and making
        sure the communication went fine.

        And, looking back at this after many years, I cannot help noticing that
        it looks a little bit funny, but I guess it did make sense, back in the
        days.

        Arguments
        ---------
        opcode : OpCode
            The opcode defining the command.

        value : int
            The actual value.

        fmt : str
            The format string.
        """
        self.write_opcode(opcode)
        logger.debug(f'Writing configuration value {value} to the serial port')
        self.pack_and_write(value, fmt)
        target_opcode = self.read_and_unpack('B')
        actual_opcode = self.read_and_unpack('B')
        actual_value = self.read_and_unpack(fmt)
        logger.debug(f'Board response ({target_opcode}, {actual_opcode}, {actual_value})...')
        if actual_opcode != opcode.value or actual_value != value:
            raise RuntimeError(f'Write/read mismatch in {self.__class__.__name__}.write_cmd()')

    def setup_analog_sampling_sketch(self, pin_list: tuple, sampling_interval: int) -> None:
        """ Setup the sktchAnalogSampling sketch.
        """
        self.write_cmd(OpCode.OP_CODE_SELECT_NUM_ANALOG_PINS, len(pin_list), 'B')
        for pin in pin_list:
            self.write_cmd(OpCode.OP_CODE_SELECT_ANALOG_PIN, pin, 'B')
        self.write_cmd(OpCode.OP_CODE_SELECT_SAMPLING_INTERVAL, sampling_interval, 'I')



class PlasduinoRunControl(RunControlBase):

    """Specialized plasduino run control.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME



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

    def open_serial_interface(self, timeout: float = None) -> None:
        """Autodetect a supported arduino board, open the serial connection to it,
        and do the handshaking.

        .. warning::
            We still have to implement to sketch upload part, here.
        """
        port = autodetect_arduino_board()
        if port is None:
            raise RuntimeError('Could not find a suitable arduino board connected.')
        self.serial_interface.connect(port, timeout=timeout)
        self.serial_interface.pulse_dtr()
        logger.info('Hand-shaking with the arduino board...')
        sketch_id = self.serial_interface.read_and_unpack('B')
        sketch_version = self.serial_interface.read_and_unpack('B')
        logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')

    def close_serial_interface(self) -> None:
        """Close the serial interface.
        """
        self.serial_interface.disconnect()



class PlasduinoAnalogEventHandler(PlasduinoEventHandler):

    """Event handler for the plasduino sketches reading analog data.
    """

    def read_packet(self) -> int:
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(AnalogReadout.SIZE)

    def read_orphan_packets(self, sleep_time: int = None) -> int:
        """
        """
        logger.info('Waiting for orphap packet(s)...')
        if sleep_time is not None:
            time.sleep(sleep_time / 1000.)
        num_bytes = self.serial_interface.in_waiting
        num_packets = num_bytes // AnalogReadout.SIZE
        if num_packets > 0:
            logger.info(f'Reading the last {num_packets} packet(s) from the serial port...')
            for i in range(num_packets):
                self.acquire_packet()
            self.flush_buffer()
        self.serial_interface.wait_rem()



class PlasduinoDigitalEventHandler(PlasduinoEventHandler):

    """Event handler for the plasduino sketches reading digital data.
    """

    def read_packet(self):
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(DigitalTransition.SIZE)
