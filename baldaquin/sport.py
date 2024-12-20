# Copyright (C) 2022--2023 the baldaquin team.
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

"""Serial port interface.
"""

import struct
import time

import serial

from baldaquin import logger


SERIAL_DATA_SIZE_DICT = {
    'c': 1,
    'b': 1,
    'B': 1,
    '?': 1,
    'h': 2,
    'H': 2,
    'i': 4,
    'I': 4,
    'l': 4,
    'L': 4,
    'q': 8,
    'Q': 8,
    'f': 4,
    'd': 8
    }



class SerialInterface(serial.Serial):

    """Small wrapper around the serial.Serial class.
    """

    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = None,
        **kwargs) -> None:
        """Constructor.
        """
        logger.info(f'Opening serial connection to port {port} @ {baudrate} baud rate...')
        super().__init__(port, baudrate, timeout=timeout, **kwargs)

    def pulse_dtr(self, pulse_length: float = 0.5) -> None:
        """Pulse the DTR line for a given amount of time.
        """
        logger.info(f'Pulsing the DTR line for {pulse_length} s...')
        self.dtr = 1
        time.sleep(pulse_length)
        self.dtr = 0

    def read_and_unpack(self, fmt: str, byte_order: str = '>'):
        """Read a given number of bytes from the serial port and unpack them.
        """
        size = SERIAL_DATA_SIZE_DICT[fmt]
        return struct.unpack(f'{byte_order}{fmt}', self.read(size))[0]

    def read_uint8(self) -> int:
        """Read an 8-bit unsigned unsigned integer from the serial port.
        """
        return self.read_and_unpack('B')

    def read_uint16(self) -> int:
        """Read a 16-bit unsigned unsigned integer from the serial port.
        """
        return self.read_and_unpack('H')

    def read_uint32(self) -> int:
        """Read a 32-bit unsigned unsigned integer from the serial port.
        """
        return self.read_and_unpack('L')

    def pack_and_write(self, value: int, fmt: str) -> int:
        """ Write a c struct to the serial port.

        For convenience, here are the basic format strings.
        Format  C type             Size
        x       pad byte
        c       char               1
        b       signed char        1
        B       unsigned char      1
        ?       _Bool              1
        h       short              2
        H       unsigned short     2
        i       int                4
        I       unsigned int       4
        l       long               4
        L       unsigned long      4
        q       long long          8
        Q       unsigned long long 8
        f       float              4
        d       double             8
        s       char[]
        p       char[]
        P       void *
        """
        return self.write(struct.pack(fmt, value))

    def write_uint8(self, value: int) -> int:
        """ Write a uint8_t to the serial port.
        """
        return self.pack_and_write(value, 'B')

    def write_uint16(self, value: int) -> int:
        """ Write a uint16_t to the serial port.
        """
        return self.pack_and_write(value, 'H')

    def write_uint32(self, value: int) -> int:
        """ Write a uint32_t to the serial port.
        """
        return self.pack_and_write(value, 'I')
