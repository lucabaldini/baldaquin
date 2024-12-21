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

"""Basic definition of the plasduino communication protocol.
"""

from dataclasses import dataclass
from enum import Enum

from baldaquin import logger
from baldaquin.event import PacketBase
from baldaquin.sport import SerialInterface



class Marker(Enum):

    """Useful protocol markers.
    """

    NO_OP_HEADER = 0xA0
    DIGITAL_TRANSITION_HEADER = 0xA1
    ANALOG_READOUT_HEADER = 0xA2
    GPS_MEASSGE_HEADER = 0xA3
    RUN_END_MARKER = 0xB0



class OpCode(Enum):

    """Definition of the opcodes from
    https://bitbucket.org/lbaldini/plasduino/src/master/arduino/protocol_h.py
    """

    OP_CODE_NO_OP = 0x00
    OP_CODE_START_RUN = 0x01
    OP_CODE_STOP_RUN = 0x02
    OP_CODE_SELECT_NUM_DIGITAL_PINS = 0x03
    OP_CODE_SELECT_DIGITAL_PIN = 0x04
    OP_CODE_SELECT_NUM_ANALOG_PINS = 0x05
    OP_CODE_SELECT_ANALOG_PIN = 0x06
    OP_CODE_SELECT_SAMPLING_INTERVAL = 0x07
    OP_CODE_SELECT_INTERRUPT_MODE = 0x08
    OP_CODE_SELECT_PWM_DUTY_CYCLE = 0x09
    OP_CODE_SELECT_POLLING_MODE = 0x0A
    OP_CODE_AD9833_CMD = 0x0B
    OP_CODE_TOGGLE_LED = 0x0C
    OP_CODE_TOGGLE_DIGITAL_PIN = 0x0D



class Polarity(Enum):

    """Polarity of a digital transition on the serial port.
    """

    RISING = 1
    FALLING = 0



@dataclass
class DigitalTransition(PacketBase):

    """A plasduino digital transition is a 6-bit binary array containing:

    * byte(s) 0  : the array header (``Marker.DIGITAL_TRANSITION_HEADER.value``);
    * byte(s) 1  : the transition information (pin number and polarity);
    * byte(s) 2-5: the timestamp of the readout from micros().
    """

    FORMAT = '>BBL'
    SIZE = PacketBase.calculate_size(FORMAT)

    header: int
    _info: int
    timestamp: float
    pin_number: int = 0
    polarity: Polarity = Polarity.RISING

    def __post_init__(self):
        """Post initialization.
        """
        if self.header != Marker.DIGITAL_TRANSITION_HEADER.value:
            raise RuntimeError(f'{self.__class__.__name__} header mismatch.')
        self.pin_number = self._info & 0x7F
        self.polarity = (self._info >> 7) & 0x1
        self.timestamp /= 1000000.



@dataclass
class AnalogReadout(PacketBase):

    """A plasduino analog readout is a 8-bit binary array containing:

    * byte(s) 0  : the array header (``Marker.ANALOG_READOUT_HEADER.value``);
    * byte(s) 1  : the analog pin number;
    * byte(s) 2-5: the timestamp of the readout from millis();
    * byte(s) 6-7: the actual adc value.
    """

    FORMAT = '>BBLH'
    SIZE = PacketBase.calculate_size(FORMAT)

    header: int
    pin_number: int
    timestamp: float
    adc_value: int

    def __post_init__(self):
        """Post initialization.

        We basically make sure that the header is correct, and we convert the timestamp
        from ms to s.
        """
        if self.header != Marker.ANALOG_READOUT_HEADER.value:
            raise RuntimeError(f'{self.__class__.__name__} header mismatch.')
        self.timestamp /= 1000.



class PlasduinoSerialInterface(SerialInterface):

    """Specialized serial interface.
    """

    def write_opcode(self, opcode):
        """
        """
        logger.debug(f'Writing {opcode} to the serial port...')
        self.write_uint8(opcode.value)

    def write_start_run(self):
        """ Write a start run command to the serial port.
        """
        self.write_opcode(OpCode.OP_CODE_START_RUN)

    def write_stop_run(self):
        """ Write a stop run command to the serial port.
        """
        self.write_opcode(OpCode.OP_CODE_STOP_RUN)

    def write_cmd(self, opcode: OpCode, value, fmt: str):
        """ Write a command to the arduino board.

        This implies writing the opcode to the serial port, writing the actual
        payload and, finally, reading back the arduino response and making
        sure the communication went fine.
        """
        self.write_opcode(opcode)
        logger.debug(f'Writing configuration value {value} to the serial port')
        self.pack_and_write(value, fmt)
        target_opcode = self.read_uint8()
        actual_opcode = self.read_uint8()
        actual_value = self.read_and_unpack(fmt)
        logger.debug(f'Board response ({target_opcode}, {actual_opcode}, {actual_value})...')
        if actual_opcode != target_opcode or actual_value != value:
            raise RuntimeError(f'Write/read mismatch in {self.__class__.__name__}.write_cmd()')

    def setup_analog_sampling_sketch(self, pin_list: tuple, sampling_interval: int):
        """ Setup the sktchAnalogSampling sketch.
        """
        self.write_cmd(OpCode.OP_CODE_SELECT_NUM_ANALOG_PINS, len(pin_list), 'B')
        for pin in pin_list:
            self.write_cmd(OpCode.OP_CODE_SELECT_ANALOG_PIN, pin, 'B')
        self.write_cmd(OpCode.OP_CODE_SELECT_SAMPLING_INTERVAL, sampling_interval, 'I')
