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

    # pylint: disable=too-many-ancestors

    def setup(self, port: str, baudrate: int = 115200, timeout: float = None) -> None:
        """Setup the serial connection.

        Arguments
        ---------
        port : str
            The name of the port to connect to (e.g., ``/dev/ttyACM0``).

        baudrate : int
            The baud rate.

            Verbatim from the pyserial documentation: the parameter baudrate can
            be one of the standard values: 50, 75, 110, 134, 150, 200, 300, 600,
            1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200. These are
            well supported on all platforms.

            Standard values above 115200, such as: 230400, 460800, 500000, 576000,
            921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000,
            4000000 also work on many platforms and devices.

            Non-standard values are also supported on some platforms (GNU/Linux,
            MAC OSX >= Tiger, Windows). Though, even on these platforms some serial
            ports may reject non-standard values.

        timeout : float
            The timeout in seconds.

            Verbatim from the pyserial documentation: possible values for the parameter
            timeout which controls the behavior of read():

            * ``timeout = None``: wait forever / until requested number of bytes
              are received

            * ``timeout = 0``: non-blocking mode, return immediately in any case,
              returning zero or more, up to the requested number of bytes

            * ``timeout = x``: set timeout to x seconds (float allowed) returns
              immediately when the requested number of bytes are available,
              otherwise wait until the timeout expires and return all bytes that
              were received until then.
        """
        logger.debug(f'Configuring serial connection (port = {port}, '
            'baudarate = {baudrate}, timeout = {timeout})...')
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

    def read_and_unpack(self, fmt: str):
        """Read a given number of bytes from the serial port and unpack them.
        """
        return struct.unpack(fmt, self.read(struct.calcsize(fmt)))[0]

    def pack_and_write(self, value: int, fmt: str) -> int:
        """ Write a value to the serial port.
        """
        return self.write(struct.pack(fmt, value))
