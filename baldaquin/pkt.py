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

"""Binary data packet utilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import struct



# Full list of supported format characters, see
# https://docs.python.org/3/library/struct.html#format-characters
_FORMAT_CHARS = ('x', 'c', 'b', 'B', '?', 'h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q',
    'n', 'N', 'e', 'f', 'd', 's', 'p', 'P')

# Characters specifying the byte order, size and alignment, as detailed in
# https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
_LAYOUT_CHARS = ('@', '=', '>', '<', '!')
_DEFAULT_LAYOUT_CHAR = _LAYOUT_CHARS[0]



class Edge(Enum):

    """Small Enum class encapsulating the edge type of a transition on a digital line.
    """

    RISING = 1
    FALLING = 0



class AbstractPacket(ABC):

    """Abstract base class for binary packets.
    """

    def __post_init__(self) -> None:
        pass

    @property
    @abstractmethod
    def payload(self) -> bytes:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def pack(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def unpack(cls, data: bytes):
        pass



class LayoutCharacterError(ValueError):

    """ValueError subclass to signal an unrecognized layout character.
    """

    def __init__(self, character: str) -> None:
        """Constructor.
        """
        super().__init__(f'Unsupported layout character \'{character}\'; '
            f'valid layout characters are {_LAYOUT_CHARS}')



class FormatCharacterError(ValueError):

    """ValueError subclass to signal an unrecognized format character.
    """

    def __init__(self, character: str) -> None:
        """Constructor.
        """
        super().__init__(f'Unsupported format character \'{character}\'; '
            f'valid format characters are {_FORMAT_CHARS}')



class FieldMismatchError(RuntimeError):

    """RuntimeError subclass to signal a field mismatch in a data structure.
    """

    def __init__(self, cls: type, field: str, expected: int, actual: int) -> None:
        """Constructor.
        """
        super().__init__(f'{cls.__name__} mismatch for field "{field}" '
            f'(expected {hex(expected)}, found {hex(actual)})')



def _check_format_characters(cls: type) -> None:
    """Check that all the format characters in the class annotations are valid.
    """
    for character in cls.__annotations__.values():
        if character not in _FORMAT_CHARS:
            raise FormatCharacterError(character)



def packetclass(cls: type) -> type:
    """Simple decorator to support automatic generation of fixed-length packet classes.
    """
    # Check that the value of the annotations are valid format characters.
    _check_format_characters(cls)

    # Make sure we have a proper packet layout.
    cls.layout = getattr(cls, 'layout', _DEFAULT_LAYOUT_CHAR)
    if cls.layout not in _LAYOUT_CHARS:
        raise LayoutCharacterError(cls.layout)

    # Cache all the necessary classvariables
    annotations = cls.__annotations__
    cls._fields = tuple(annotations.keys())
    cls._format = f'{cls.layout}{"".join(annotations.values())}'
    cls._size = struct.calcsize(cls._format)

    # Create the class constructor.
    def _init(self, *args, payload: bytes = None):
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

            #@property
            #def _getter(self):
            #    return value

            #self.__setattr__(field, _getter.getter)

            self.__setattr__(field, value)
        if payload is None:
            payload = self.pack()
        self.__setattr__('_payload', payload)
        # Make sure the post-initialization is correctly performed.
        self.__post_init__()

    # Create the __str__ dunder method.
    def _str(self):
        attrs = self._fields + ('payload', '_format')
        info = ', '.join([f'{attr}={getattr(self, attr)}' for attr in attrs])
        return f'{self.__class__.__name__}({info})'

    # Attach the dunder methods to the class and we are good to go.
    cls.__init__ = _init
    cls.__str__ = _str
    return cls



@packetclass
class FixedSizePacketBase(AbstractPacket):

    @property
    def payload(self) -> bytes:
        return self._payload

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        return (getattr(self, field) for field in self._fields)

    def pack(self) -> bytes:
        return struct.pack(self._format, *self)

    @classmethod
    def unpack(cls, data: bytes) -> AbstractPacket:
        return cls(*struct.unpack(cls._format, data), payload=data)



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
