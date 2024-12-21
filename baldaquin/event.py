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

"""Event handler.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Any

from loguru import logger

from baldaquin.__qt__ import QtCore
from baldaquin.buf import CircularBuffer



@dataclass
class EventBase:

    """Virtual base class with possible event structure.

    Concrete subclasses should define the relevant fields for the event, using
    the dataclass machinery, and override the ``FORMAT`` class member

    .. warning::

       Mind that the ``FORMAT`` should match the type and the order of
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
    FORMAT = None
    SIZE = None

    @staticmethod
    def calculate_size(fmt: str) -> int:
        """Calculate the size of a structure in bytes, given a format string.

        This is provided as a usefull shortcut for simple cases when the event structure
        is simply defined as a format string, and the size can be calculated by
        the Python struct module.
        """
        return struct.calcsize(fmt)

    def __len__(self) -> int:
        """Default dunder method for indicating the size of the event in bytes.
        """
        return self.SIZE

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
        return struct.pack(self.FORMAT, *self.attribute_values())

    @classmethod
    def unpack(cls, data : bytes) -> EventBase:
        """Unpack some data into an event object.
        """
        return cls(*struct.unpack(cls.FORMAT, data))

    @classmethod
    def read_from_file(cls, input_file) -> EventBase:
        """Read a single event from a file object open in binary mode.
        """
        return cls.unpack(input_file.read(struct.calcsize(cls.FORMAT)))



@dataclass
class EventStatistics:

    """Small container class helping with the event handler bookkeeping.
    """

    events_processed : int = 0
    events_written : int = 0
    bytes_written : int = 0

    def reset(self) -> None:
        """Reset the statistics.
        """
        self.events_processed = 0
        self.events_written = 0
        self.bytes_written = 0

    def update(self, events_processed, events_written, bytes_written) -> None:
        """Update the event statistics.
        """
        self.events_processed += events_processed
        self.events_written += events_written
        self.bytes_written += bytes_written



class EventHandlerBase(QtCore.QObject, QtCore.QRunnable):

    # pylint: disable=c-extension-no-member

    """Base class for an event handler.

    This is an abstract base class inheriting from ``QtCore.QRunnable``, owning
    a data buffer that can be used to cache data, and equipped with a binary flag
    that allows for syncronization.
    """

    BUFFER_CLASS = CircularBuffer
    BUFFER_KWARGS = {}

    #pylint: disable=c-extension-no-member
    output_file_set = QtCore.Signal(Path)

    def __init__(self) -> None:
        """Constructor.

        Note that, apparently, the order of inheritance is important when emitting
        signals from a QRunnable---you want to call the QObject constructor first,
        see the last comment at
        https://forum.qt.io/topic/72818/how-can-i-emit-signal-from-qrunnable-or-call-callback

        Also, in order for the event handler not to be automatically deleted
        when `QtCore.QThreadPool.globalInstance().waitForDone()` is called,
        we need to test the autoDelete flag to False, see
        https://doc.qt.io/qtforpython/PySide6/QtCore/QRunnable.html
        """
        # Make sure we call the QObject constructor first.
        QtCore.QObject.__init__(self)
        QtCore.QRunnable.__init__(self)
        # Set the autoDelete flag to False so that we can restart the event
        # handler multiple times.
        self.setAutoDelete(False)
        # Create the event buffer.
        self._buffer = self.BUFFER_CLASS(**self.BUFFER_KWARGS)
        self._statistics = EventStatistics()
        self.__running = False

    def statistics(self) -> EventStatistics:
        """Return the underlying EventStatistics object.
        """
        return self._statistics

    def reset_statistics(self) -> None:
        """Reset the underlying statistics.
        """
        self._statistics.reset()

    def set_output_file(self, file_path : Path) -> None:
        """Set the path to the output file.
        """
        self._buffer.set_output_file(file_path)
        self.output_file_set.emit(file_path)

    def flush_buffer(self) -> None:
        """Write all the buffer data to disk.
        """
        events_written, bytes_written = self._buffer.flush()
        self._statistics.update(0, events_written, bytes_written)

    def run(self):
        """Overloaded QRunnable method.
        """
        # At this point the buffer should be empty, as we should have hd a flush()
        # call at the stop of the previous run.
        if self._buffer.size() > 0:
            logger.warning('Event buffer is not empty at the start run, clearing it...')
            self._buffer.clear()
        # Update the __running flag and enter the event loop.
        self.__running = True
        while self.__running:
            event_data = self.read_event_data()
            self._buffer.put(event_data)
            self._statistics.update(1, 0, 0)
            if self._buffer.flush_needed():
                self.flush_buffer()
            self.process_event_data(event_data)

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def read_event_data(self) -> Any:
        """Read a single event (must be overloaded in derived classes).

        This is the actual blocking function that gets a single event from the hardware.
        """
        raise NotImplementedError
