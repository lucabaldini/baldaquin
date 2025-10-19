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

import struct
import time
from dataclasses import dataclass
from typing import Any

import serial
import serial.tools.list_ports
import serial.tools.list_ports_common

from .logging_ import logger

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

    def __hash__(self):
        """Hash function.
        """
        return hash((self.vid, self.pid))

    def __repr__(self) -> str:
        """String formatting.
        """
        return f"(vid={self._hex(self.vid)}, pid={self._hex(self.pid)})"


@dataclass
class PortInfo:

    """Small data class holding the information about a COM port.

    This is a simple wrapper around the serial.tools.list_ports_common.ListPortInfo
    isolating the basic useful functionalities, for the sake of simplicity. (And,
    in addition, this convenience class is meant to integrate the functionality
    embedded in the :class:`DeviceId` class, which is handy.)

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
    def from_serial(cls, port_info: serial.tools.list_ports_common.ListPortInfo) -> PortInfo:
        """Create a Port object from a ListPortInfo object.
        """
        device_id = DeviceId(port_info.vid, port_info.pid)
        return cls(port_info.device, device_id, port_info.manufacturer)


def list_com_ports(*device_ids: DeviceId) -> list[PortInfo]:
    """List all the com ports with devices attached, possibly with a filter on
    the device ids we are interested into.

    Arguments
    ---------
    device_ids : DeviceId or vid, pid tuples, optional
        An arbitrary number of device ids to filter the list of ports returned by pyserial.
        This is useful when we are searching for a specific device attached to a
        port; an arduino uno, e.g., might look something like (0x2341, 0x43).

    Returns
    -------
    list of PortInfo objects
        The list of COM ports.
    """
    logger.info("Scanning serial devices...")
    # Populate the initial list of ports.
    ports = [PortInfo.from_serial(item) for item in serial.tools.list_ports.comports()]
    for port_info in ports:
        logger.debug(port_info)
    logger.info(f"Done, {len(ports)} device(s) found.")
    # If we're not filtering over device ids, we're done.
    if len(device_ids) == 0:
        return ports
    # Otherwise, we filter the list of ports, assuming we have any.
    if len(ports) > 0:
        # If we have a list of tuples, we convert them to DeviceId objects---this
        # will make the printout on the terminal nicer, with the 0x and all that.
        device_ids = list(device_ids)
        for i, entry in enumerate(device_ids):
            if isinstance(entry, tuple):
                device_ids[i] = DeviceId(*entry)
        logger.info(f"Filtering port list for specific devices: {device_ids}...")
        # Do the actual filtering.
        ports = [port_info for port_info in ports if port_info.device_id in device_ids]
        logger.info(f"Done, {len(ports)} device(s) remaining.")
    for port in ports:
        logger.debug(port)
    return ports


class TextLine(bytearray):

    """Small class defining a simple protocol for passing messages in string form
    over the serial port.

    A message is basically a small piece of text, in the form of a binary stream
    encoded in UTF-8, starting with a ``#`` header character and terminated by a line
    feed, and that can contain an arbitrary number of fields separated by a ``;``.
    Note the delimiters are properly checked at creation time.
    The :meth:`unpack()` class method returns a tuple with the field values,
    converted in the proper types.

    Note this is a subclass of the bytearray class, as opposed to the bytes class,
    because we provide a minimal support for prepending and appending fields to the
    text line. (Insertion at a generic index does not make much sense, as the field
    widths are variable.)

    The choice of the header character and the line feed is largely arbitrary, but
    the requirement that the line is terminated by a line feed provides the most
    straightforward way to read variable-length messages from the serial port in
    a reliable way, leveraging the serial ``readline()`` method.

    Users should by no means feel compelled to use this, but we provide it in order
    to facilitate passing strings over the serial port, saving boilerplate code
    for runtime checking.

    Example
    -------
    >>> message = TextLine.from_text("#Hello world;1\\n")
    >>> name, version = message.unpack(str, int)
    >>> print(name, type(name))
    Hello world, <class 'str'>
    >>> print(version, type(version))
    1 <class 'int'>
    """

    _ENCODING = "utf-8"
    _HEADER = "#"
    _HEADER_ORD = ord(_HEADER)
    _LINE_FEED = "\n"
    _LINE_FEED_ORD = ord(_LINE_FEED)
    _SEPARATOR = ";"

    def __init__(self, data: bytes) -> None:
        """Constructor.
        """
        super().__init__(data)
        if len(data) == 0:
            raise RuntimeError(f"Empty buffer passed to the {self.__class__.__name__} constructor")
        if not self[0] == self._HEADER_ORD:
            raise RuntimeError(f"Serial text line {self} does not start with {self._HEADER}")
        if not self[-1] == self._LINE_FEED_ORD:
            raise RuntimeError(f"Serial text line {self} does not end with a line feed")

    @classmethod
    def from_text(cls, text: str) -> bytes:
        """Create a message from a text string (mainly for debug purposes).
        """
        return cls(bytes(text, cls._ENCODING))

    def prepend(self, value: str) -> None:
        """Prepend a string field to the text line.

        Arguments
        ---------
        value : str
            The string to be prepended.
        """
        self[1:1] = bytes(f"{value}{self._SEPARATOR}", self._ENCODING)

    def append(self, value: str) -> None:
        """Append a string field to the text line.

        Arguments
        ---------
        value : str
            The string to be prepended.
        """
        self[-1:-1] = bytes(f"{self._SEPARATOR}{value}", self._ENCODING)

    def unpack(self, *converters) -> tuple:
        """Unpack the message in its (properly formatted) fields.

        Arguments
        ---------
        arguments : callable
            The converter functions to be used to unpack the fields. Note the number
            of converters passed to the function must be either zero (in which case
            all the fields are treated as strings) or equal to the number of fields
            in the message. A RuntimeError is raised if that is not the case.
        """
        # Decode the relevant part of the underlying bytes object (i.e., everything
        # but the header character and the line feed) and split the resulting string
        # by the separator character.
        fields = self[1:-1].decode(self._ENCODING).split(self._SEPARATOR)
        # Convert the fields to the proper types, if any.
        if len(converters) == 0:
            pass
        elif len(converters) == len(fields):
            fields = [converter(field) for converter, field in zip(converters, fields)]
        else:
            raise RuntimeError(f'Need exactly 0 or {len(fields)} converters to unpack "{self}"')
        # Return the fields as a tuple.
        return tuple(fields)


class SerialInterface(serial.Serial):

    """Small wrapper around the serial.Serial class.

    Note the class is designed to be instantiated without arguments, and all the
    setup is done through the :meth:`connect()` method, where the port is configured
    and the actual connection is opened.
    """

    # pylint: disable=too-many-ancestors

    def __init__(self) -> None:
        """Do-nothing constructor.
        """
        super().__init__()
        self.port_info = None

    def connect(self, port_info: PortInfo, baudrate: int = DEFAULT_BAUD_RATE,
                timeout: float = None) -> None:
        """Setup the serial connection.

        Note that the first argument is a fully-fledged PortInfo object, which
        allows to keep track of the basic information about the device connected
        to the port, in addition to configuration of the port itself. This is
        handy, e.g., for the auto-upload of arduino sketched, where we need to
        know the designation of the board we are uploading to.

        Arguments
        ---------
        port_info : PortInfo
            The PortInfo object describing the port.

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
        logger.debug(f"Configuring serial connection (port = {port_info.name}, "
                     f"baudarate = {baudrate}, timeout = {timeout})...")
        self.port_info = port_info
        self.port = port_info.name
        self.baudrate = baudrate
        self.timeout = timeout
        logger.info(f"Opening serial connection to port {self.port}...")
        self.open()

    def set_timeout(self, timeout: float) -> None:
        """Set the timeout for the serial port.

        Arguments
        ---------
        timeout : float
            The timeout in seconds.
        """
        logger.info(f"Setting serial connection timeout to {timeout} s...")
        self.timeout = timeout

    def disconnect(self):
        """Disconnect from the serial port.
        """
        logger.info(f"Closing serial connection to port {self.port}...")
        self.close()

    def pulse_dtr(self, pulse_length: float = 0.5) -> None:
        """Pulse the DTR line for a given amount of time.

        This asserts the DTR line, waits for a specific amount of time, and then
        de-asserts the line.

        Arguments
        ---------
        pulse_length : float
            The duration (in seconds) for the DTR line signal to be asserted.
        """
        logger.info(f"Pulsing the DTR line for {pulse_length} s...")
        self.dtr = 1
        time.sleep(pulse_length)
        self.dtr = 0

    def read_available_data(self) -> bytes:
        """Read all the available data on the serial interface.

        .. warning::
            Be cautious when using this method, as the amount of data available
            on the serial port at any given time may depend on the exact timing of
            the function call relative to what the device attached to the port is
            doing, and in the long run it might be difficult to read a stream
            of variable-length data reliably.
        """
        return self.read(self.in_waiting)

    def read_text_line(self) -> TextLine:
        """Read a line-feed terminated string data from the serial interface and return a
        :class:`TextLine` object.
        """
        return TextLine(self.readline())

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
        >>> val = s.read_and_unpack("B") # Single byte (val is int)
        >>> val = s.read_and_unpack(">L") # Big-endian unsigned long (val is also int)
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
