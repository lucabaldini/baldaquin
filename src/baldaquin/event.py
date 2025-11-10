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

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .__qt__ import QtCore
from .buf import CircularBuffer, WriteMode
from .logging_ import logger
from .pkt import AbstractPacket, PacketStatistics


class EventHandlerBase(QtCore.QObject, QtCore.QRunnable):

    """Base class for an event handler.

    This is an abstract base class inheriting from ``QtCore.QRunnable``, owning
    a data buffer that can be used to cache data, and equipped with a binary flag
    that allows for syncronization.
    """

    BUFFER_CLASS = CircularBuffer

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
        self._buffer = self.BUFFER_CLASS()
        self._statistics = PacketStatistics()
        self.__running = False

    def configure_buffer(self, *args):
        """Convenience method to configure the underlying buffer.
        """
        self._buffer.configure(*args)

    def statistics(self) -> PacketStatistics:
        """Return the underlying PacketStatistics object.
        """
        return self._statistics

    def reset_statistics(self) -> None:
        """Reset the underlying statistics.
        """
        self._statistics.reset()

    def set_primary_sink(self, file_path: Path) -> None:
        """Set the primary sink for the buffer.
        """
        self._buffer.set_primary_sink(file_path)
        self.output_file_set.emit(file_path)

    def add_custom_sink(self, file_path: Path, mode: WriteMode, formatter: Callable = None,
                        header: Any = None) -> None:
        """Add a custom sink to the underlying packet buffer.
        """
        self._buffer.add_custom_sink(file_path, mode, formatter, header)

    def disconnect_sinks(self) -> None:
        """Disconnect all sinks from the underlying packet buffer.
        """
        self._buffer.disconnect_sinks()

    def flush_buffer(self) -> None:
        """Write all the buffer data to disk.
        """
        packets_written, bytes_written = self._buffer.flush()
        self._statistics.update(0, packets_written, bytes_written)

    def acquire_packet(self) -> None:
        """Acquire a single packet.

        This is the inner function that gets execute within the run() method, and
        it is factored out so that, if necessary, it can be called in a stand-alone
        fashion, rather than automatically when the data acquisition thread is
        launched.

        .. warning::
            We need some cleanup, here, to make sure we really thought through the
            mechanism for defining the ``process_packet()`` slot.
        """
        packet_data = self.read_packet()
        self._buffer.put(self.process_packet(packet_data))
        self._statistics.update(1, 0, 0)
        if self._buffer.flush_needed():
            self.flush_buffer()

    def run(self):
        """Overloaded QRunnable method.
        """
        # At this point the buffer should be empty, as we should have hd a flush()
        # call at the stop of the previous run.
        if self._buffer.size() > 0:
            logger.warning("Event buffer is not empty at the start run, clearing it...")
            self._buffer.clear()
        self.__running = True
        while self.__running:
            self.acquire_packet()

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def read_packet(self) -> AbstractPacket:
        """Read a single packet (must be overloaded in derived classes).

        This is the actual blocking function that gets a single event from the hardware.
        """
        raise NotImplementedError

    # def process_packet(self, packet: AbstractPacket) -> None:
    #     """Process a single packet (must be overloaded in derived classes).
    #
    #     This is typically implemented downstream in the user application.
    #     """
    #     raise NotImplementedError
