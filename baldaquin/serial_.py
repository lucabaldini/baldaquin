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
from typing import Any

import serial
import serial.tools.list_ports
import serial.tools.list_ports_common

from baldaquin import logger


# List of standard baud rates.
STANDARD_BAUD_RATES = serial.Serial.BAUDRATES
DEFAULT_BAUD_RATE = 115200


def _fmt_port(port: serial.tools.list_ports_common.ListPortInfo) -> str:
    """Small convenience function to print out some pretty-printed serial port info.
    """
    text = port.device
    vid, pid, manufacturer = port.vid, port.pid, port.manufacturer
    if vid is None and pid is None:
        return text
    text = f'{text} -> vid {hex(vid)}, pid {hex(pid)}'
    if manufacturer is not None:
        text = f'{text} by {manufacturer}'
    return text


def list_com_ports(*devices) -> serial.tools.list_ports_common.ListPortInfo:
    """List all the com ports with devices attached, possibly with a filter on the
    (vid, pid) pairs we are interested into.

    Arguments
    ---------
    *devices : (vid, pid) tuples
        The (vid, pid) tuples to filter the list of ports returned by pyserial.
        This is useful when we are searching for a specific device attached to a
        port; an arduino uno, e.g., might look something like (0x2341, 0x43).

    Returns
    -------
    list of serial.tools.list_ports_common.ListPortInfo
        See
        https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
        for the object documentation.
    """
    logger.info('Scanning serial devices...')
    ports = serial.tools.list_ports.comports()
    for port in ports:
        logger.debug(_fmt_port(port))
    logger.info(f'Done, {len(ports)} device(s) found.')
    if len(ports) > 0:
        device_list = [f'({hex(vid)}, {hex(pid)})' for vid, pid in devices]
        logger.info(f'Filtering port list for specific devices: {", ".join(device_list)}...')
        ports = [port for port in ports if (port.vid, port.pid) in devices]
        logger.info(f'Done, {len(ports)} device(s) remaining.')
    for port in ports:
        logger.debug(_fmt_port(port))
    return ports


class SerialInterface(serial.Serial):

    """Small wrapper around the serial.Serial class.
    """

    # pylint: disable=too-many-ancestors

    def setup(self, port: str, baudrate: int = DEFAULT_BAUD_RATE, timeout: float = None) -> None:
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
                     f'baudarate = {baudrate}, timeout = {timeout})...')
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def connect(self, port: str, baudrate: int = 115200, timeout: float = None) -> None:
        """Connect to the serial port.

        Arguments
        ---------
        port : str
            The name of the serial port (e.g., ``/dev/ttyACM0``).

        baudrate : int
            The baud rate.

        timeout : float, optional
            The timeout in seconds.
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

        This asserts the DTR line, waits for a specific amount of time, and then
        deasserts the line.

        Arguments
        ---------
        pulse_length : float
            The duration (in seconds) for the DTR line signal to be asserted.
        """
        logger.info(f'Pulsing the DTR line for {pulse_length} s...')
        self.dtr = 1
        time.sleep(pulse_length)
        self.dtr = 0

    def read_and_unpack(self, fmt: str) -> Any:
        """Read a given number of bytes from the serial port and unpack them.

        Note that the number of bytes to be read from the serial port is automatically
        calculated from the format string.
        See https://docs.python.org/3/library/struct.html for all the details about
        format strings and byte ordering.

        Arguments
        ---------
        fmt : str
            The format string for the packet to be read from the seria port.

        Returns
        -------
        any
            Returns the proper Python object for the format string at hand.

        Example
        -------
        >>> s = SerialInterface(port)
        >>> val = s.read_and_unpack('B') # Single byte (val is int)
        >>> val = s.read_and_unpack('>L') # Big-endian unsigned long (val is also int)
        """
        data = self.read(struct.calcsize(fmt))
        try:
            return struct.unpack(fmt, data)[0]
        except struct.error as exception:
            logger.error(f'Could not unpack {data} with format "{fmt}".')
            raise exception

    def pack_and_write(self, value: Any, fmt: str) -> int:
        """ Pack a given value into a proper bytes object and write the latter
        to the serial port.

        Arguments
        ---------
        value : any
            The value to be written to the serial port.

        fmt : str
            The format string to pack the value with.

        Returns
        -------
        int
            The number of bytes written to the serial port.
        """
        return self.write(struct.pack(fmt, value))
