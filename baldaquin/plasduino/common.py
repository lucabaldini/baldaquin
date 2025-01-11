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

import struct
import time
from typing import Any

from baldaquin import arduino_
from baldaquin import logger
from baldaquin import plasduino
from baldaquin.app import UserApplicationBase
from baldaquin.buf import CircularBuffer
from baldaquin.config import ConfigurationBase
from baldaquin.event import EventHandlerBase
from baldaquin.pkt import AbstractPacket
from baldaquin.plasduino.protocol import Marker, OpCode, AnalogReadout, DigitalTransition
from baldaquin.plasduino.shields import Lab1
from baldaquin.runctrl import RunControlBase
from baldaquin.serial_ import SerialInterface
from baldaquin.strip import SlidingStripChart


# List of supported boards, i.e., only the arduino uno at the moment.
_SUPPORTED_BOARDS = (arduino_.UNO, )


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

    def read_run_end_marker(self) -> None:
        """Read a single byte from the serial port and make sure it is the
        run-end marker.

        (The run end marker is sent over through the serial port from the arduino
        sketch when the run is stopped and all the measurements have been completed,
        and needs to be taken out of the way in order for the next run to take place.)
        """
        logger.info('Waiting for the run end marker...')
        marker = self.read_and_unpack('B')
        if not marker == Marker.RUN_END_MARKER.value:
            raise RuntimeError(f'Run end marker mismatch '
                  f'(expected {hex(Marker.RUN_END_MARKER.value)}, found {hex(marker)}).')
        logger.info('Run end marker correctly read.')

    def read_until_run_end_marker(self, timeout: float = None) -> None:
        """Read data from the serial port until the end-of-run marker is found.

        This is actually never used, as the intermediate data would get lost, but
        it is potentially useful when debugging the serial communication.

        Arguments
        ---------
        timeout : float (default None)
            The timeout (in s) to be temporarily set for the transaction.
        """
        logger.info('Scanning serial input for run-end marker...')
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

        Arguments
        ---------
        opcode : OpCode
            The operational code to be written to the serial port.
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

    def setup_analog_sampling_sketch(self, sampling_interval: int) -> None:
        """ Setup the sktchAnalogSampling sketch.

        Note that we are taking a minimal approach, here, where exactly two input
        analog pins are used, and they are those dictated by the Lab 1 shield, i.e.,
        the only thing that we are setting, effectively, is the sampling interval.

        Arguments
        ---------
        sampling_interval : int
            The sampling interval in ms.
        """
        self.write_cmd(OpCode.OP_CODE_SELECT_NUM_ANALOG_PINS, len(Lab1.ANALOG_PINS), 'B')
        for pin in Lab1.ANALOG_PINS:
            self.write_cmd(OpCode.OP_CODE_SELECT_ANALOG_PIN, pin, 'B')
        self.write_cmd(OpCode.OP_CODE_SELECT_SAMPLING_INTERVAL, sampling_interval, 'I')


class PlasduinoRunControl(RunControlBase):

    """Specialized plasduino run control.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME


class PlasduinoEventHandlerBase(EventHandlerBase):

    """Plasduino basic event handler.

    This takes care of all the operations connected with the handshaking and
    sketch upload. Derived classes must implement the ``read_packet()`` slot.
    """

    BUFFER_CLASS = CircularBuffer
    BUFFER_KWARGS = dict(max_size=1000, flush_size=100, flush_interval=5.)

    def __init__(self) -> None:
        """Constructor.

        Note we create an empty serial interface, here, and we then open the port
        while setting up the user application.
        """
        super().__init__()
        self.serial_interface = PlasduinoSerialInterface()

    def open_serial_interface(self, timeout: float = None) -> None:
        """Autodetect a supported arduino board, open the serial connection to it,
        and do the handshaking.

        .. warning::
            We still have to implement to sketch upload part, here.

        Arguments
        ---------
        timeout : float (default None)
            The timeout (in s) for the serial readout. If set to None, every read
            operation is effectively blocking, and this is the way we should operate
            in normal conditions.
        """
        port = arduino_.autodetect_arduino_board(*_SUPPORTED_BOARDS)
        if port is None:
            raise RuntimeError('Could not find a suitable arduino board connected.')
        self.serial_interface.connect(port.device, timeout=timeout)
        self.serial_interface.pulse_dtr()
        logger.info('Hand-shaking with the arduino board...')
        sketch_id = self.serial_interface.read_and_unpack('B')
        sketch_version = self.serial_interface.read_and_unpack('B')
        logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')

    def close_serial_interface(self) -> None:
        """Close the serial interface.
        """
        self.serial_interface.disconnect()

    def process_packet(self, packet: AbstractPacket) -> None:
        """Overloaded method.
        """
        raise NotImplementedError


class PlasduinoAnalogEventHandler(PlasduinoEventHandlerBase):

    """Event handler for the plasduino sketches reading analog data.
    """

    def read_packet(self) -> int:
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(AnalogReadout.size)

    def wait_pending_packets(self, sleep_time: int = None) -> int:
        """Wait and read all the pending packets from the serial port, then consume
        the run end marker.

        This is necessary because, after the sketch running on the arduino board
        receives the run end opcode, there is a varible number of analog readouts
        (ranging from 0 to 2 if 2 pins are used) that are acquired before the
        data acquisition is actually stopped. (Yes, poor design on the sketch side.)
        What we do here is essentially: wait a long enough time (it should be
        equal or longer than the sampling time to catch all the corner cases),
        see how many bytes are waiting in the input buffer of the serial port,
        calculate the number of pending packets, read them and finally consume the
        run end marker, so that we are ready to start again.

        Note that the pending packets are correctly processed, passed to the
        event handler buffer and written to disk.

        Arguments
        ---------
        sleep_time : int (default None)
            The amount of time (in ms) we wait before polling the serial port
            for additional pending packets.
        """
        logger.info('Waiting for pending packet(s)...')
        if sleep_time is not None:
            time.sleep(sleep_time / 1000.)
        num_bytes = self.serial_interface.in_waiting
        # At this point we expect a number of events which is a multiple of
        # AnalogReadout.size, + 1. If this is not the case, it might indicate that
        # we have not waited enough.
        if num_bytes % AnalogReadout.size != 1:
            logger.warning(f'{num_bytes} pending on the serial port, expected 1, 9 or 17...')
        num_packets = num_bytes // AnalogReadout.size
        if num_packets > 0:
            logger.info(f'Reading the last {num_packets} packet(s) from the serial port...')
            for _ in range(num_packets):
                self.acquire_packet()
            self.flush_buffer()
        self.serial_interface.read_run_end_marker()

    def process_packet(self, packet: AbstractPacket) -> None:
        """Overloaded method.
        """
        raise NotImplementedError


class PlasduinoDigitalEventHandler(PlasduinoEventHandlerBase):

    """Event handler for the plasduino sketches reading digital data.
    """

    def read_packet(self):
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(DigitalTransition.size)

    def process_packet(self, packet: AbstractPacket) -> None:
        """Overloaded method.
        """
        raise NotImplementedError


class PlasduinoAnalogConfiguration(ConfigurationBase):

    """User application configuration for plasduino analog applications.
    """

    PARAMETER_SPECS = (
        ('strip_chart_max_length', 'int', 200, 'Strip chart maximum length',
            dict(min=10, max=1000000)),
    )


class PlasduinoAnalogUserApplicationBase(UserApplicationBase):

    """Specialized base class for plasduino user applications relying on the
    sktchAnalogSampling.ino sketch.
    """

    _SAMPLING_INTERVAL = None

    @staticmethod
    def create_strip_charts(ylabel: str = 'ADC counts'):
        """Create all the strip charts for displaying real-time data.
        """
        kwargs = dict(xlabel='Time [s]', ylabel=ylabel)
        return {pin: SlidingStripChart(label=f'Pin {pin}', **kwargs) for pin in Lab1.ANALOG_PINS}

    def configure(self):
        """Overloaded method.
        """
        raise NotImplementedError

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()
        self.event_handler.serial_interface.setup_analog_sampling_sketch(self._SAMPLING_INTERVAL)

    def teardown(self) -> None:
        """Overloaded method (STOPPED -> RESET).
        """
        self.event_handler.close_serial_interface()

    def start_run(self) -> None:
        """Overloaded method (STOPPED -> RUNNING).
        """
        self.event_handler.serial_interface.write_start_run()
        super().start_run()

    def stop_run(self) -> None:
        """Overloaded method (RUNNING -> STOPPED).
        """
        super().stop_run()
        self.event_handler.serial_interface.write_stop_run()
        self.event_handler.wait_pending_packets(self._SAMPLING_INTERVAL)
