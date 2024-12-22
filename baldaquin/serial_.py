# Copyright (C) 2022--2024 the baldaquin team.
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



class SerialInterface(serial.Serial):

    """Small wrapper around the serial.Serial class.
    """

    def setup(self, port: str, baudrate: int = 115200, timeout: float = None) -> None:
        """Setup the connection.
        """
        logger.debug(f'Configuring serial connection (port = {port}, baudarate = {baudrate}, timeout = {timeout})...')
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def connect(self, port: str, baudrate: int = 115200, timeout: float = None) -> None:
        """Connect to the serial port.
        """
        self.setup(port, baudrate, timeout)
        logger.info(f'Opening serial connection to port {self.port}...')
        self.open()

    def disconnect(self):
        """Disconnect from the serial port.
        """
        logger.info(f'Closing serial connection to port {self.port}...')
        self.close()

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
        return struct.unpack(f'{byte_order}{fmt}', self.read(struct.calcsize(fmt)))[0]

    def pack_and_write(self, value: int, fmt: str) -> int:
        """ Write a value to the serial port.
        """
        return self.write(struct.pack(fmt, value))
