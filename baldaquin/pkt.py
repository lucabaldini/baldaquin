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

"""Binary data packet utilities.
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import struct

from baldaquin import logger
from baldaquin.timeline import Timeline


class Format(Enum):

    """Enum class encapsulating the supporte format characters from
    https://docs.python.org/3/library/struct.html#format-characters
    """

    PAD_BTYE = 'x'
    CHAR = 'c'
    SIGNED_CHAR = 'b'
    UNSIGNED_CHAR = 'B'
    BOOL = '?'
    SHORT = 'h'
    UNSIGNED_SHORT = 'H'
    INT = 'i'
    UNSIGNED_INT = 'I'
    LONG = 'l'
    UNSIGNED_LONG = 'L'
    LONG_LONG = 'q'
    UNSIGNED_LONG_LONG = 'Q'
    SSIZE_T = 'n'
    SIZE_T = 'N'
    FLOAT = 'f'
    DOUBLE = 'd'


class Layout(Enum):

    """Enum class encapsulating the supported layout characters from
    https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
    """

    NATIVE_SIZE = '@'
    NATIVE = '='
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'
    NETWORK = '!'
    DEFAULT = '@'


class Edge(Enum):

    """Small Enum class encapsulating the edge type of a transition on a digital line.
    """

    RISING = 1
    FALLING = 0


class AbstractPacket(ABC):

    """Abstract base class for binary packets.
    """

    COMMENT_PREFIX = '# '
    TEXT_SEPARATOR = ', '

    def __post_init__(self) -> None:
        """Hook for post-initialization.
        """

    @property
    @abstractmethod
    def data(self) -> bytes:
        """Return the packet binary data.
        """

    @property
    @abstractmethod
    def fields(self) -> tuple:
        """Return the packet fields.
        """

    @abstractmethod
    def __len__(self) -> int:
        """Return the length of the binary data in bytes.
        """

    @abstractmethod
    def __iter__(self):
        """Iterate over the field values.
        """

    @abstractmethod
    def pack(self) -> bytes:
        """Pack the field values into the corresponding binary data.
        """

    @classmethod
    @abstractmethod
    def unpack(cls, data: bytes):
        """Unpack the binary data into the corresponding field values.
        """

    @classmethod
    def text_header(cls) -> str:
        """Hook that subclasses can overload to provide a sensible header for an
        output text file.
        """
        return f'{cls.COMMENT_PREFIX}Created on {Timeline().latch()}'

    def to_text(self) -> str:
        """Hook that subclasses can overload to provide a text representation of
        the buffer to be written in an output text file.
        """
        raise NotImplementedError


class FieldMismatchError(RuntimeError):

    """RuntimeError subclass to signal a field mismatch in a data structure.
    """

    def __init__(self, cls: type, field: str, expected: int, actual: int) -> None:
        """Constructor.
        """
        super().__init__(f'{cls.__name__} mismatch for field "{field}" '
                         f'(expected {hex(expected)}, found {hex(actual)})')


def _class_annotations(cls) -> dict:
    """Small convienience function to retrieve the class annotations.

    This is needed because in Python 3.7 cls.__annotations__ is not defined
    when a class has no annotations, while in subsequent Python versions an empty
    dictionary is returned, instead.
    """
    try:
        return cls.__annotations__
    except AttributeError:
        return {}


def _check_format_characters(cls: type) -> None:
    """Check that all the format characters in the class annotations are valid.
    """
    for character in _class_annotations(cls).values():
        if not isinstance(character, Format):
            raise ValueError(f'Format character {character} is not a Format value')


def _check_layout_character(cls: type) -> None:
    """Check that the class layout character is valid.
    """
    cls.layout = getattr(cls, 'layout', Layout.DEFAULT)
    if not isinstance(cls.layout, Layout):
        raise ValueError(f'Layout character {cls.layout} is not a Layout value')


def packetclass(cls: type) -> type:
    """Simple decorator to support automatic generation of fixed-length packet classes.
    """
    # pylint: disable = protected-access
    _check_format_characters(cls)
    _check_layout_character(cls)
    # Cache all the necessary classvariables
    annotations = _class_annotations(cls)
    cls._fields = tuple(annotations.keys())
    cls._format = f'{cls.layout.value}{"".join(char.value for char in annotations.values())}'
    cls.size = struct.calcsize(cls._format)
    # And here is a list of attributes we want to be frozen.
    cls.__frozenattrs__ = ('_fields', '_format', 'size', '_data') + cls._fields

    def _init(self, *args, data: bytes = None):
        # Make sure we have the correct number of arguments---they should match
        # the class annotations.
        if len(args) != len(cls._fields):
            raise TypeError(f'{cls.__name__}.__init__() expected {len(cls._fields)} '
                            f'arguments {cls._fields}, got {len(args)}')
        # Loop over the annotations and create all the instance variables.
        for field, value in zip(cls._fields, args):
            # If a given annotation has a value attched to it, make sure we are
            # passing the same thing.
            expected = getattr(cls, field, None)
            if expected is not None and expected != value:
                raise FieldMismatchError(cls, field, expected, value)
            object.__setattr__(self, field, value)
        if data is None:
            data = self.pack()
        object.__setattr__(self, '_data', data)
        # Make sure the post-initialization is correctly performed.
        self.__post_init__()

    cls.__init__ = _init
    return cls


@packetclass
class FixedSizePacketBase(AbstractPacket):

    """Class describing a packet with fixed size.
    """

    # All of these fields will be overwritten by the @packetclass decorator, but
    # we list them here for reference, and to make pylint happy.
    _fields = None
    _format = None
    size = 0
    __frozenattrs__ = None
    _data = None

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def fields(self) -> tuple:
        return self._fields

    def __len__(self) -> int:
        return self.size

    def __iter__(self):
        return (getattr(self, field) for field in self.fields)

    def pack(self) -> bytes:
        return struct.pack(self._format, *self)

    @classmethod
    def unpack(cls, data: bytes) -> AbstractPacket:
        return cls(*struct.unpack(cls._format, data), data=data)

    def __setattr__(self, key, value) -> None:
        """Overloaded method to make class instances frozen.
        """
        if key in self.__class__.__frozenattrs__:
            raise AttributeError(f'Cannot modify {self.__class__.__name__}.{key}')
        object.__setattr__(self, key, value)

    def __repr__(self):
        """String formatting.
        """
        attrs = self._fields + ('data', '_format')
        info = ', '.join([f'{attr}={getattr(self, attr)}' for attr in attrs])
        return f'{self.__class__.__name__}({info})'

    @classmethod
    def text_header(cls) -> str:
        """Overloaded method.
        """
        return f'{super().text_header()}\n' \
               f'{cls.COMMENT_PREFIX}{cls.TEXT_SEPARATOR.join(cls._fields)}\n'

    def to_text(self) -> str:
        """Overloaded method.
        """
        return f'{self.TEXT_SEPARATOR.join([str(item) for item in self])}\n'


class PacketFile:

    """Class describing a binary file containing packets.
    """

    def __init__(self, packet_class: type) -> None:
        """Constructor.
        """
        self._packet_class = packet_class
        self._input_file = None

    @contextmanager
    def open(self, file_path: str):
        """Open the file.
        """
        logger.debug(f'Opening input packet file {file_path}...')
        with open(file_path, 'rb') as input_file:
            self._input_file = input_file
            yield self
            self._input_file = None
        logger.debug(f'Input file {file_path} closed.')

    def __iter__(self) -> 'PacketFile':
        """Return the iterator object (self).
        """
        return self

    def __next__(self) -> FixedSizePacketBase:
        """Read the next packet in the buffer.
        """
        data = self._input_file.read(self._packet_class.size)
        if not data:
            raise StopIteration
        return self._packet_class.unpack(data)

    def read_all(self) -> tuple[FixedSizePacketBase]:
        """Read in memory all the packets in the file.

        This is meant to support postprocessing applications where one needs
        all the packets in memory at the same time. Use it `cum grano salis`.
        """
        return tuple(packet for packet in self)


@dataclass
class PacketStatistics:

    """Small container class helping with the event handler bookkeeping.
    """

    packets_processed: int = 0
    packets_written: int = 0
    bytes_written: int = 0

    def reset(self) -> None:
        """Reset the statistics.
        """
        self.packets_processed = 0
        self.packets_written = 0
        self.bytes_written = 0

    def update(self, packets_processed, packets_written, bytes_written) -> None:
        """Update the event statistics.
        """
        self.packets_processed += packets_processed
        self.packets_written += packets_written
        self.bytes_written += bytes_written
