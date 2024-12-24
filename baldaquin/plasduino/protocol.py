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
import struct

from baldaquin import logger
from baldaquin.event import PacketBase



class Marker(Enum):

    """Relevant protocol markers, verbatim from
    https://bitbucket.org/lbaldini/plasduino/src/master/arduino/protocol.h

    (In the old days we used to have this generated automatically from the
    corresponding header file, but the project is so stable now, that this seems
    hardly relevant.)
    """

    NO_OP_HEADER = 0xA0
    DIGITAL_TRANSITION_HEADER = 0xA1
    ANALOG_READOUT_HEADER = 0xA2
    GPS_MEASSGE_HEADER = 0xA3
    RUN_END_MARKER = 0xB0



class OpCode(Enum):

    """Definition of the operational codes, verbatim from
    https://bitbucket.org/lbaldini/plasduino/src/master/arduino/protocol.h

    (In the old days we used to have this generated automatically from the
    corresponding header file, but the project is so stable now, that this seems
    hardly relevant.)
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

    """Polarity of a digital transition on the serial port---this indicate whether
    the timestamp was acquired on the rising or falling edge of the input signal.
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
    HEADER_MARKER = Marker.DIGITAL_TRANSITION_HEADER.value

    header: int
    _info: int
    timestamp: float
    pin_number: int = 0
    polarity: Polarity = Polarity.RISING

    def __post_init__(self) -> None:
        """Post initialization.

        We make sure that the header is correct, unpack the _info field, and
        convert the timestamp from us to s.
        """
        if self.header != self.HEADER_MARKER:
            logger.error(f'Expected {hex(self.HEADER_MARKER)}, got {hex(self.header)}...')
            raise RuntimeError(f'{self.__class__.__name__} header mismatch.')
        # Note the _info field is packing into a single byte the polarity
        # (the MSB) and the pin number.
        self.pin_number = self._info & 0x7F
        self.polarity = (self._info >> 7) & 0x1
        self.timestamp /= 1.e6



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
    HEADER_MARKER = Marker.ANALOG_READOUT_HEADER.value

    header: int
    pin_number: int
    timestamp: float
    adc_value: int

    def __post_init__(self) -> None:
        """Post initialization.

        We make sure that the header is correct, and we convert the timestamp
        from ms to s.
        """
        if self.header != self.HEADER_MARKER:
            logger.error(f'Expected {hex(self.HEADER_MARKER)}, got {hex(self.header)}...')
            raise RuntimeError(f'{self.__class__.__name__} header mismatch.')
        self.timestamp /= 1.e3
