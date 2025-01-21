# Copyright (C) 2022--2025 the baldaquin team.
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

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class DeviceId:

    """Data class to hold the device id information.

    A device id is basically a tuple of two integers, the vendor id (vid) and the
    product id (pid), and the class has exactly these two members.

    Arguments
    ---------
    vid : int
        The vendor id.

    pid : int
        The product id.
    """

    vid: int
    pid: int

    def __eq__(self, other) -> bool:
        """Equality comparison.

        Note we support the comparison between a DeviceId object and a tuple.
        """
        if isinstance(other, tuple):
            return (self.vid, self.pid) == other
        return (self.vid, self.pid) == (other.vid, other.pid)

    @staticmethod
    def _hex(value: int) -> str:
        """Convenience function to format an integer as a hexadecimal string,
        gracefully handling the case when the input is not an integer.
        """
        try:
            return hex(value)
        except TypeError:
            return None

    def __repr__(self) -> str:
        """String formatting.
        """
        return f'(vid={self._hex(self.vid)}, pid={self._hex(self.pid)})'


@dataclass
class Port:

    """Small data class holding the informatio about a COM port.

    This is a simple wrapper around the serial.tools.list_ports_common.ListPortInfo
    isolating the basic useful functionalities, for the sake of simplicity.

    See https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
    for more information.

    Arguments
    ---------
    name : str
        The name of the port (e.g., ``/dev/ttyACM0``).

    device_id : DeviceId
        The device id.

    manufacturer : str, optional
        The manufacturer of the device attached to the port.
    """

    name: str
    device_id: DeviceId
    manufacturer: str = None

    @classmethod
    def from_port_info(cls, port_info: serial.tools.list_ports_common.ListPortInfo) -> 'Port':
        """Create a Port object from a ListPortInfo object.
        """
        device_id = DeviceId(port_info.vid, port_info.pid)
        return cls(port_info.device, device_id, port_info.manufacturer)


def list_com_ports(device_ids: list[DeviceId] = None) -> list[Port]:
    """List all the com ports with devices attached, possibly with a filter on
    the device ids we are interested into.

    Arguments
    ---------
    device_ids : list of DeviceId objects or vid, pid tuples, optional
        The list of device ids to filter the list of ports returned by pyserial.
        This is useful when we are searching for a specific device attached to a
        port; an arduino uno, e.g., might look something like (0x2341, 0x43).

    Returns
    -------
    list of Port objects
        The list of COM ports.
    """
    logger.info('Scanning serial devices...')
    # Populate the initial list of ports.
    ports = [Port.from_port_info(port_info) for port_info in serial.tools.list_ports.comports()]
    for port in ports:
        logger.debug(port)
    logger.info(f'Done, {len(ports)} device(s) found.')
    # If we're not filtering over device ids, we're done.
    if device_ids is None:
        return ports
    # Otherwise, we filter the list of ports, assuming we have any.
    if len(ports) > 0:
        # If we have a list of tuples, we convert them to DeviceId objects---this
        # will make the printout on the terminal nicer, with the 0x and all that.
        # Note that, since we are changing the list in place, we need to make 
        # sure it is actually a list and not an immutable sequence.
        if not isinstance(device_ids, list):
            device_ids = list(device_ids)
        for i, entry in enumerate(device_ids):
            if isinstance(entry, tuple):
                device_ids[i] = DeviceId(*entry)
        logger.info(f'Filtering port list for specific devices: {device_ids}...')
        # Do the actual filtering.
        ports = [port for port in ports if port.device_id in device_ids]
        logger.info(f'Done, {len(ports)} device(s) remaining.')
    for port in ports:
        logger.debug(port)
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
