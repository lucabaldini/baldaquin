# Copyright (C) 2022 the baldaquin team.
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

"""Event handler.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import struct
from typing import Any

from baldaquin.buf import CircularBuffer
from baldaquin._qt import QtCore



@dataclass
class EventBase:

    """Virtual base class with possible event structure.

    Concrete subclasses should define the relevant fields for the event, using
    the dataclass machinery, and override the ``FORMAT_STRING`` class member

    .. warning::

       Mind that the ``FORMAT_STRING`` should match the type and the order of
       the event fields fields. The format string is passed verbatim to the
       Python ``struct`` module, and the related information is available at
       https://docs.python.org/3/library/struct.html

    The basic idea, here, is that the :meth:`pack() <baldaquin.event.EventBase.pack()>`
    method returns a bytes object that can be written into a binary file,
    while the :meth:`unpack() <baldaquin.event.EventBase.unpack()>` method does
    the opposite, i.e., it constructs an event object from its binary representation
    (the two are designed to round-trip). Additionally, the
    :meth:`read_from_file() <baldaquin.event.EventBase.read_from_file()>`
    method reads and unpack one event from file.
    """

    # pylint: disable=invalid-name
    FORMAT_STRING = None

    def attribute_values(self) -> tuple:
        """Return the values for all the attributes, to be used, e.g., in the
        ``pack()`` method.

        See, e.g., https://stackoverflow.com/questions/69090253/ for more
        information about how to programmatically iterate over dataclass fields.
        Since this is not necessarily blazingly fast, we provide the functionality
        wrapped in a small function, so that subclasses can overaload it if
        needed.
        """
        return tuple(getattr(self, field.name) for field in dataclasses.fields(self))

    def pack(self) -> bytes:
        """Pack the event for supporting binary output to file.
        """
        return struct.pack(self.FORMAT_STRING, *self.attribute_values())

    @classmethod
    def unpack(cls, data : bytes) -> EventBase:
        """Unpack some data into an event object.
        """
        return cls(*struct.unpack(cls.FORMAT_STRING, data))

    @classmethod
    def read_from_file(cls, input_file) -> EventBase:
        """Read a single event from a file object open in binary mode.
        """
        return cls.unpack(input_file.read(struct.calcsize(cls.FORMAT_STRING)))




class EventHandlerBase(QtCore.QRunnable):

    # pylint: disable=c-extension-no-member

    """Base class for an event handler.

    This is an abstract base class inheriting from ``QtCore.QRunnable``, owning
    a data buffer that can be used to cache data, and equipped with a binary flag
    that allows for syncronization.

    Arguments
    ---------
    file_path : str
        The path to the output file.

    buffer_class : type
        The class to be used to instantiate the event buffer object.

    kwargs : dict
        Keyword arguents for the data buffer creation.
    """

    BUFFER_CLASS = CircularBuffer

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        self.buffer = None
        self.__running = False

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def flush_buffer(self):
        """
        """
        self.buffer.flush()

    def setup(self, file_path : str, **kwargs) -> None:
        """
        """
        self.buffer = self.BUFFER_CLASS(file_path, **kwargs)

    def run(self) -> None:
        """Overloaded QRunnable method.
        """
        self.__running = True
        while self.__running:
            self.buffer.put_item(self.process_event())

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
