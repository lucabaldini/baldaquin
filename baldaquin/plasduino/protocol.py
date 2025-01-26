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

from enum import Enum, IntEnum

from baldaquin.pkt import packetclass, AbstractPacket, FixedSizePacketBase, Format, Layout


COMMENT_PREFIX = '# '
TEXT_SEPARATOR = ', '


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


class InterruptMode(IntEnum):

    """Definition of the interrupt modes.
    """

    DISABLED = 0
    CHANGE = 1
    FALLING = 2
    RISING = 3


@packetclass
class AnalogReadout(FixedSizePacketBase):

    """A plasduino analog readout is a 8-byte binary array containing:

    * byte(s) 0  : the array header (``Marker.ANALOG_READOUT_HEADER.value``);
    * byte(s) 1  : the analog pin number;
    * byte(s) 2-5: the timestamp of the readout from millis();
    * byte(s) 6-7: the actual adc value.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = Marker.ANALOG_READOUT_HEADER.value
    pin_number: Format.UNSIGNED_CHAR
    milliseconds: Format.UNSIGNED_LONG
    adc_value: Format.UNSIGNED_SHORT

    def __post_init__(self) -> None:
        """Post initialization.
        """
        self.seconds = 1.e-3 * self.milliseconds

    # pylint: disable=arguments-differ
    @staticmethod
    def text_header(label: str) -> str:
        """Return the header for the output text file.
        """
        return f'{AbstractPacket.text_header()}' \
               f'{COMMENT_PREFIX}Pin number{TEXT_SEPARATOR}Time [s]' \
               f'{TEXT_SEPARATOR}{label}\n'

    def to_text(self) -> str:
        """Convert a readout to text for use in a custom sink.

        Note that this is potentially tricky, as if any conversion is required
        downstream (e.g., if we are reading a temperature), we might end up needing
        to define a custom class anyway.
        """
        return f'{self.pin_number}{TEXT_SEPARATOR}{self.seconds:.3f}' \
               f'{TEXT_SEPARATOR}{self.adc_value}\n'

    def __str__(self):
        """String formatting.

        Note that we are overloading the `__str__()` method, leaving alone the
        default `__repr__()` dunder from the base class.
        """
        return self._repr(('pin_number', 'seconds', 'adc_value'), ('%d', '%.6f', '%d'))


@packetclass
class DigitalTransition(FixedSizePacketBase):

    """A plasduino digital transition is a 6-byte binary array containing:

    * byte(s) 0  : the array header (``Marker.DIGITAL_TRANSITION_HEADER.value``);
    * byte(s) 1  : the transition information (pin number and edge type);
    * byte(s) 2-5: the timestamp of the readout from micros().
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = Marker.DIGITAL_TRANSITION_HEADER.value
    info: Format.UNSIGNED_CHAR
    microseconds: Format.UNSIGNED_LONG

    def __post_init__(self) -> None:
        """Post initialization.
        """
        # Note the _info field is packing into a single byte the edge type
        # (the MSB) and the pin number.
        self.pin_number = self.info & 0x7F
        self.edge = (self.info >> 7) & 0x1
        self.seconds = 1.e-6 * self.microseconds

    @staticmethod
    def text_header() -> str:
        """Return the header for the output text file.
        """
        return f'{AbstractPacket.text_header()}' \
               f'{COMMENT_PREFIX}Time [s]{TEXT_SEPARATOR}Edge type\n'

    def to_text(self) -> str:
        """Convert a temperature readout to text for use in a custom sink.
        """
        return f'{self.seconds:.6f}{TEXT_SEPARATOR}{self.edge}\n'

    def __str__(self):
        """String formatting.

        Note that we are overloading the `__str__()` method, leaving alone the
        default `__repr__()` dunder from the base class.
        """
        return self._repr(('pin_number', 'edge', 'seconds'), ('%d', '%d', '%.6f'))
