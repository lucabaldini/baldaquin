# Copyright (C) 2024--2025 the baldaquin team.
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

from enum import IntEnum

from baldaquin.pkt import AbstractPacket, FixedSizePacketBase, Format, Layout, packetclass

COMMENT_PREFIX = '# '
TEXT_SEPARATOR = ', '


class Marker(IntEnum):

    """Relevant protocol markers, verbatim from
    https://bitbucket.org/lbaldini/plasduino/src/master/arduino/protocol.h

    (In the old days we used to have this generated automatically from the
    corresponding header file, but the project is so stable now, that this seems
    hardly relevant.)
    """

    NO_OP_HEADER = 0xa0
    DIGITAL_TRANSITION_HEADER = 0xa1
    ANALOG_READOUT_HEADER = 0xa2
    GPS_MEASSGE_HEADER = 0xa3
    RUN_END_MARKER = 0xb0


class OpCode(IntEnum):

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
    OP_CODE_SELECT_POLLING_MODE = 0x0a
    OP_CODE_AD9833_CMD = 0x0b
    OP_CODE_TOGGLE_LED = 0x0c
    OP_CODE_TOGGLE_DIGITAL_PIN = 0x0d


class InterruptMode(IntEnum):

    """Definition of the interrupt modes.
    """

    DISABLED = 0
    CHANGE = 1
    FALLING = 2
    RISING = 3


@packetclass
class PlasduinoPacketBase(FixedSizePacketBase):

    """Base class for the plasduino packets.
    """

    OUTPUT_HEADERS = None
    OUTPUT_ATTRIBUTES = None
    OUTPUT_FMTS = None

    @classmethod
    def text_header(cls, prefix: str = COMMENT_PREFIX, creator: str = None) -> str:
        """Return the header for the output text file.
        """
        headers = ', '.join(map(str, cls.OUTPUT_HEADERS))
        return f'{AbstractPacket.text_header(prefix, creator)}{prefix}{headers}\n'

    def to_text(self, separator: str = TEXT_SEPARATOR) -> str:
        """Convert a readout to text for use in a custom sink.
        """
        return self._text(self.OUTPUT_ATTRIBUTES, self.OUTPUT_FMTS, separator)

    def __str__(self):
        """String formatting.
        """
        return self._repr(self.OUTPUT_ATTRIBUTES, self.OUTPUT_FMTS)


@packetclass
class AnalogReadout(PlasduinoPacketBase):

    """A plasduino analog readout is a 8-byte binary array containing:

    * byte(s) 0  : the array header (``Marker.ANALOG_READOUT_HEADER``);
    * byte(s) 1  : the analog pin number;
    * byte(s) 2-5: the timestamp of the readout from millis();
    * byte(s) 6-7: the actual adc value.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = Marker.ANALOG_READOUT_HEADER
    pin_number: Format.UNSIGNED_CHAR
    milliseconds: Format.UNSIGNED_LONG
    adc_value: Format.UNSIGNED_SHORT

    OUTPUT_HEADERS = ('Pin number', 'Time [s]', 'ADC counts')
    OUTPUT_ATTRIBUTES = ('pin_number', 'seconds', 'adc_value')
    OUTPUT_FMTS = ('%d', '%.3f', '%d')

    def __post_init__(self) -> None:
        """Post initialization.
        """
        self.seconds = 1.e-3 * self.milliseconds


@packetclass
class DigitalTransition(PlasduinoPacketBase):

    """A plasduino digital transition is a 6-byte binary array containing:

    * byte(s) 0  : the array header (``Marker.DIGITAL_TRANSITION_HEADER``);
    * byte(s) 1  : the transition information (pin number and edge type);
    * byte(s) 2-5: the timestamp of the readout from micros().
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = Marker.DIGITAL_TRANSITION_HEADER
    info: Format.UNSIGNED_CHAR
    microseconds: Format.UNSIGNED_LONG

    OUTPUT_HEADERS = ('Pin number', 'Edge type', 'Time [s]')
    OUTPUT_ATTRIBUTES = ('pin_number', 'edge', 'seconds')
    OUTPUT_FMTS = ('%d', '%d', '%.6f')

    def __post_init__(self) -> None:
        """Post initialization.
        """
        # Note the _info field is packing into a single byte the edge type
        # (the MSB) and the pin number.
        self.pin_number = self.info & 0x7F
        self.edge = (self.info >> 7) & 0x1
        self.seconds = 1.e-6 * self.microseconds
