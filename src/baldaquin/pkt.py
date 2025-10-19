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

from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, IntEnum

from . import __version__
from .logging_ import logger
from .timeline import Timeline

DEFAULT_TEXT_PREFIX = "#"
DEFAULT_TEXT_SEPARATOR = ","


class Format(Enum):

    """Enum class encapsulating the supporte format characters from
    https://docs.python.org/3/library/struct.html#format-characters
    """

    PAD_BTYE = "x"
    CHAR = "c"
    SIGNED_CHAR = "b"
    UNSIGNED_CHAR = "B"
    BOOL = "?"
    SHORT = "h"
    UNSIGNED_SHORT = "H"
    INT = "i"
    UNSIGNED_INT = "I"
    LONG = "l"
    UNSIGNED_LONG = "L"
    LONG_LONG = "q"
    UNSIGNED_LONG_LONG = "Q"
    SSIZE_T = "n"
    SIZE_T = "N"
    FLOAT = "f"
    DOUBLE = "d"


class Layout(Enum):

    """Enum class encapsulating the supported layout characters from
    https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
    """

    NATIVE_SIZE = "@"
    NATIVE = "="
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"
    NETWORK = "!"
    DEFAULT = "@"


class Edge(IntEnum):

    """Small Enum class encapsulating the edge type of a transition on a digital line.
    """

    RISING = 1
    FALLING = 0


class AbstractPacket(ABC):

    """Abstract base class for binary packets.
    """

    def __post_init__(self) -> None: # noqa: B027
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

    def _format_attributes(self, attrs: tuple[str], fmts: tuple[str] = None) -> tuple[str]:
        """Helper function to join a given set of class attributes in a properly
        formatted string.

        This is used, most notably, in the :meth:`_repr() <baldaquin.pkt.AbstractPacket._repr>`
        hook below, which in turn is used in the various ``__repr__()`` and/or ``__str__``
        implementations, and in the :meth:`to_text() <baldaquin.pkt.AbstractPacket.to_text>`
        implementations in sub-classes.

        Arguments
        ---------
        attrs : tuple
            The names of the class attributes we want to include in the representation.

        fmts : tuple, optional
            If present determines the formatting of the given attributes.
        """
        vals = (getattr(self, attr) for attr in attrs)
        if fmts is None:
            fmts = ("%s" for _ in attrs)
        return tuple(fmt % val for val, fmt in zip(vals, fmts))

    def _text(self, attrs: tuple[str], fmts: tuple[str], separator: str) -> str:
        """Helper function for text formatting.

        Note the output includes a trailing endline.

        Arguments
        ---------
        attrs : tuple
            The names of the class attributes we want to include in the representation.

        fmts : tuple,
            Determines the formatting of the given attributes.

        separator : str
            The separator between different fields.
        """
        vals = self._format_attributes(attrs, fmts)
        return f"{separator.join(vals)}\n"

    def _repr(self, attrs: tuple[str], fmts: tuple[str] = None) -> str:
        """Helper function to provide sensible string formatting for the packets.

        The basic idea is that concrete classes would use this to implement their
        `__repr__()` and/or `__str__()` special dunder methods.

        Arguments
        ---------
        attrs : tuple
            The names of the class attributes we want to include in the representation.

        fmts : tuple, optional
            If present determines the formatting of the given attributes.
        """
        vals = self._format_attributes(attrs, fmts)
        info = ", ".join([f"{attr}={val}" for attr, val in zip(attrs, vals)])
        return f"{self.__class__.__name__}({info})"

    @classmethod
    def text_header(cls, prefix: str = DEFAULT_TEXT_PREFIX, creator: str = None) -> str:
        """Hook that subclasses can overload to provide a sensible header for an
        output text file.

        Arguments
        ---------
        prefix : str
            The prefix to be prepended to each line to signal that that line is
            a comment and contains no data.

        creator : str, optional
            An optional string indicating the application that created the file.
        """
        header = f"{prefix}Created on {Timeline().latch()}\n" \
                 f"{prefix}baldaquin version: {__version__}\n"
        if creator is not None:
            header = f"{header}{prefix}Creator: {creator}\n"
        return header

    def to_text(self, separator: str = DEFAULT_TEXT_SEPARATOR) -> str:
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
                         f"(expected {hex(expected)}, found {hex(actual)})")


def _class_annotations(cls) -> dict:
    """Small convienience function to retrieve the class annotations.

    Note that, in order to support inheritance of @packetclasses, we do iterate
    over all the ancestors of the class at hand, starting from ``AbstractPacket``,
    and collect all the annotations along the way. The iteration is in reverse
    order, so that the final order of annotations is what one would expect.

    The try/except clause is needed because in Python 3.7 cls.__annotations__ is
    not defined when a class has no annotations, while in subsequent Python
    versions an empty dictionary is returned, instead.
    """
    # The typical mro, here, is object -> ABC -> AbstractPacket -> ...
    # Although object and ABC seem to have no annotations, and might very well
    # never have one, we only start the annotation-collection loop from
    # AbstractPacket, so that the situation is under our full control (cross your)
    # fingers.
    ancestors = cls.__mro__[:cls.__mro__.index(AbstractPacket)]
    annotations = {}
    for _cls in reversed(ancestors):
        try: # noqa: SIM105
            annotations.update(_cls.__annotations__)
        except AttributeError: #noqa: PERF203
            pass
    return annotations


def _check_format_characters(cls: type) -> None:
    """Check that all the format characters in the class annotations are valid.
    """
    for character in _class_annotations(cls).values():
        if not isinstance(character, Format):
            raise ValueError(f"Format character {character} is not a Format value")


def _check_layout_character(cls: type) -> None:
    """Check that the class layout character is valid.
    """
    cls.layout = getattr(cls, "layout", Layout.DEFAULT)
    if not isinstance(cls.layout, Layout):
        raise ValueError(f"Layout character {cls.layout} is not a Layout value")


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
    cls.__frozenattrs__ = ("_fields", "_format", "size", "_data") + cls._fields

    def _init(self, *args, data: bytes = None):
        # Make sure we have the correct number of arguments---they should match
        # the class annotations.
        if len(args) != len(cls._fields):
            raise TypeError(f"{cls.__name__}.__init__() expected {len(cls._fields)} "
                            f"arguments {cls._fields}, got {len(args)}")
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
        object.__setattr__(self, "_data", data)
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
            raise AttributeError(f"Cannot modify {self.__class__.__name__}.{key}")
        object.__setattr__(self, key, value)

    def __repr__(self):
        """String formatting.

        Note that this provides the low-level string formatting, according to the
        typical Python conventions. Subclasses are welcome to provide more
        succinct and human-readable `__str__()` special dunder implementations, but
        are encouraged not to reimplement this special method, as it inclues all
        the nitty-gritty details of the packet, which might be useful when debugging.
        """
        return self._repr(self._fields + ("data", "_format"))

    def __str__(self):
        """String formatting.

        This is a slightly more concise test representation of the packet. Again,
        subclasses can reimplement this at their leisure.
        """
        return self._repr(self._fields)

    @classmethod
    def text_header(cls, prefix: str = DEFAULT_TEXT_PREFIX, creator: str = None) -> str:
        """Overloaded method.
        """
        return f"{AbstractPacket.text_header(prefix, creator)}" \
               f'{prefix}{", ".join(cls._fields)}\n'

    def to_text(self, separator: str = DEFAULT_TEXT_SEPARATOR) -> str:
        """Overloaded method.
        """
        return f"{separator.join([str(item) for item in self])}\n"


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
        logger.debug(f"Opening input packet file {file_path}...")
        with open(file_path, "rb") as input_file:
            self._input_file = input_file
            yield self
            self._input_file = None
        logger.debug(f"Input file {file_path} closed.")

    def __iter__(self) -> PacketFile:
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

    def to_dict(self) -> dict:
        """Serialization.
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, **kwargs) -> PacketStatistics:
        """Deserialization.
        """
        return cls(**kwargs)
