# Copyright (C) 2022--2023 the baldaquin team.
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

"""Data buffering.
"""

from __future__ import annotations

import collections
import io
import queue
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any

from .env import BALDAQUIN_ENCODING
from .logging_ import logger
from .pkt import AbstractPacket
from .profile import timing


class WriteMode(Enum):

    """Small enum class for the file write mode.

    Note this has to match the open modes in the Python open() builtin.
    """

    BINARY = "b"
    TEXT = "t"


class Sink:

    """Small class describing a file sink where a buffer can be flushed.

    Arguments
    ---------
    file_path : Path or str
        The path to the output file.

    mode : WriteMode
        The write mode (``WriteMode.BINARY`` or ``WriteMode.TEXT``)

    formatter : callable, optional
        The packet formatting function to be used to flush a buffer.

    header : anything that can be written to the output file
        The file optional file header. If not None, this gets written to the
        output file when the sink is created.
    """

    def __init__(self, file_path: Path, mode: WriteMode, formatter: Callable = None,
                 header: Any = None) -> None:
        """Constructor.
        """
        # If the output file already exists, then something has gone wrong---we
        # never overwrite data.
        if file_path.exists():
            raise FileExistsError(f"Output file {file_path} already exists")
        self.file_path = file_path
        self.formatter = formatter
        self._mode = mode
        self._output_file = None
        # Note we always open the output file in append mode.
        self._open_kwargs = dict(mode=f"a{self._mode.value}")
        if self._mode == WriteMode.TEXT:
            self._open_kwargs.update(encoding=BALDAQUIN_ENCODING)
        # At this point we do create the file and, if needed, we write the
        # header into it. (And we are ready to flush.)
        with self.open() as output_file:
            if header is not None:
                logger.debug("Writing file header...")
                output_file.write(header)

    @contextmanager
    def open(self) -> io.IOBase:
        """Open the proper file object and return it.

        Note this is implemented as a context manager, and yields a reference to
        the underlying (open) output file.
        """
        # pylint: disable=unspecified-encoding, bad-open-mode
        logger.debug(f"Opening output file {self.file_path} {self._open_kwargs}...")
        output_file = open(self.file_path, **self._open_kwargs) # noqa SIM115
        yield output_file
        output_file.close()
        logger.debug(f"Ouput file {self.file_path} closed.")

    def __str__(self) -> str:
        """String formatting.
        """
        if self.formatter is None:
            return f"Sink -> {self.file_path} ({self._mode})"
        return f"Sink -> {self.file_path} ({self._mode}, {self.formatter.__qualname__})"


class AbstractBuffer(ABC):

    """Abstract base class for a data buffer.

    Arguments
    ---------
    flush_size : int
        The maximum number of packets before a
        :meth:`flush_needed() <baldaquin.buf.AbstractBuffer.flush_needed()>`
        call returns True.

    flush_timeout : float
        The maximum time (in s) elapsed since the last
        :meth:`flush() <baldaquin.buf.AbstractBuffer.flush()>` before a
        :meth:`flush_needed() <baldaquin.buf.AbstractBuffer.flush_needed()>` call
        returns True.
    """

    def __init__(self, flush_size: int, flush_timeout: float) -> None:
        """Constructor.
        """
        self._flush_size = flush_size
        self._flush_timeout = flush_timeout
        self._last_flush_time = time.time()
        self._primary_sink = None
        self._custom_sinks = []

    def configure(self, flush_size: int, flush_timeout: float) -> None:
        """Configure the buffer parameters.
        """
        logger.info(f"Configuring {self.__class__.__name__} with flush_size={flush_size}, "
                    f"flush_timeout={flush_timeout} s...")
        self._flush_size = flush_size
        self._flush_timeout = flush_timeout

    def put(self, packet: AbstractPacket) -> None:
        """Put a packet into the buffer.

        Note we check in the abstract class that the packet we put into the buffer
        is an ``AbstractPacket`` instance, while the actual work is done in the
        ``_do_put()`` method, that is abstract and should be reimplemented in all
        derived classes.
        """
        if not isinstance(packet, AbstractPacket):
            raise TypeError(f"{packet} is not an AbstractPacket instance")
        self._do_put(packet)

    @abstractmethod
    def _do_put(self, packet: AbstractPacket) -> None:
        """Abstract method with the actual code to put a packet into the buffer
        (to be reimplemented in derived classes).

        .. warning::
            In case you wonder why this is called ``_do_put`` and not, e.g., ``_put()``...
            well: whoever designed the ``queue.Queue`` class (which we rely on for
            of the actual buffer implementations) apparently had the same brilliant
            idea of delegating the ``put()`` call to a ``_put()`` function, and
            overloading that name was putting things into an infinite loop.
        """

    @abstractmethod
    def pop(self) -> Any:
        """Pop an item from the buffer (to be reimplemented in derived classes).

        .. note::
            The specific semantic of `which` item is returned (e.g, the first,
            last, or something more clever) is delegated to the concrete classes,
            but we will be mostly dealing with FIFOs, i.e., unless otherwise
            stated it should be understood that this is popping items from the
            left of the queue.
        """

    @abstractmethod
    def size(self) -> int:
        """Return the number of items in the buffer (to be reimplemented in derived classes).
        """

    @abstractmethod
    def clear(self) -> None:
        """Clear the buffer (to be reimplemented in derived classes).
        """

    def almost_full(self) -> bool:
        """Return True if the buffer is almost full.
        """
        return self._flush_size is not None and self.size() >= self._flush_size

    def time_since_last_flush(self):
        """Return the time (in s) since the last flush operation, or since the
        buffer creation, in case it has never been flushed.
        """
        return time.time() - self._last_flush_time

    def flush_needed(self) -> bool:
        """Return True if the buffer needs to be flushed.
        """
        return self.almost_full() or self.time_since_last_flush() > self._flush_timeout

    def set_primary_sink(self, file_path: Path) -> Sink:
        """Set the primary sink for the buffer.
        """
        sink = Sink(file_path, WriteMode.BINARY, None, None)
        logger.info(f"Connecting buffer to primary {sink}...")
        self._primary_sink = sink
        return sink

    def add_custom_sink(self, file_path: Path, mode: WriteMode, formatter: Callable = None,
                        header: Any = None) -> Sink:
        """Add a sink to the buffer.

        See the :class:`Sink <baldaquin.buf.Sink>` class constructor for an
        explanation of the arguments.
        """
        sink = Sink(file_path, mode, formatter, header)
        logger.info(f"Connecting buffer to custom {sink}...")
        self._custom_sinks.append(sink)
        return sink

    def disconnect(self) -> None:
        """Disconnect all sinks.
        """
        self._primary_sink = None
        self._custom_sinks = []
        logger.info("All buffer sinks disconnected.")

    def _pop_and_write_raw(self, num_packets: int, output_file: io.IOBase) -> int:
        """Pop the first ``num_packets`` packets from the buffer and write the
        corresponding raw binary data into the given output file.

        Arguments
        ---------
        num_packets : int
            The number of packets to be written out.

        output_file : io.IOBase
            The output binary file.

        Returns
        -------
        int
            The number of bytes written to disk.
        """
        num_bytes_written = 0
        for _ in range(num_packets):
            num_bytes_written += output_file.write(self.pop().data)
        logger.debug(f"{num_bytes_written} bytes written to disk.")
        return num_bytes_written

    def _write(self, num_packets: int, output_file: io.IOBase, formatter: Callable) -> int:
        """Write the first ``num_packets`` packets from the buffer to the given
        output file (and with the given formatter) without popping them.

        Arguments
        ---------
        num_packets : int
            The number of packets to be written out.

        output_file : io.IOBase
            The output binary file.

        formatter : Callable
            The packet formatting function.

        Returns
        -------
        int
            The number of bytes written to disk.
        """
        num_bytes_written = 0
        for i in range(num_packets):
            num_bytes_written += output_file.write(formatter(self[i]))
        logger.debug(f"{num_bytes_written} bytes written to disk.")
        return num_bytes_written

    @timing
    def flush(self) -> tuple[int, int]:
        """Write the content of the buffer to all the sinks connected.

        .. note::
           This will write all the items in the buffer at the time of the
           function call, i.e., items added while writing to disk will need to
           wait for the next call.
        """
        if self._primary_sink is None:
            raise RuntimeError("No primary sink connected to the buffer, cannot flush")
        # Cache the number of packets to be read---this is implemented this way
        # as we might be adding new packets while flushing the buffer.
        num_packets = self.size()
        num_bytes_written = 0
        self._last_flush_time = time.time()
        # If there are no packets, then there is nothing to do, and we are not
        # actually flushing the buffer.
        if num_packets == 0:
            return (num_packets, num_bytes_written)
        # And, finally, the actual flush.
        logger.info(f"{num_packets} packets ready to be written out...")
        # First write to all the custom sinks, as this does not empty the buffer...
        for sink in self._custom_sinks:
            with sink.open() as output_file:
                num_bytes_written += self._write(num_packets, output_file, sink.formatter)
        # ... and, finally flush the buffer to the primary sink.
        with self._primary_sink.open() as output_file:
            num_raw_bytes_written = self._pop_and_write_raw(num_packets, output_file)
            num_bytes_written += num_raw_bytes_written
        logger.info(f"{num_bytes_written} bytes ({num_raw_bytes_written} raw bytes) "
                    "written to disk.")
        # Note at this point we are keeping track of both the total number of
        # bytes written to disk *and* the number of bytes written in the form of
        # raw binary packets, and we can decide which one we want to use downstream,
        # e.g., to update the GUI.
        return (num_packets, num_bytes_written)


class FIFO(queue.Queue, AbstractBuffer):

    """Implementation of a FIFO.

    This is using the `queue <https://docs.python.org/3/library/queue.html>`_
    module in the Python standard library.

    Note that the queue.Queue class is internally using a collections.deque
    object, so this is effectively another layer of complexity over the
    CircularBuffer class below. It's not entirely clear to me what the real
    difference would be, in a multi-threaded context.
    """

    def __init__(self, flush_size: int = None, flush_timeout: float = 10.) -> None:
        """Constructor.
        """
        # From the stdlib documentation: maxsize is an integer that sets the
        # upper bound limit on the number of items that can be placed in the queue.
        # If maxsize is less than or equal to zero, the queue size is infinite.
        queue.Queue.__init__(self, -1)
        AbstractBuffer.__init__(self, flush_size, flush_timeout)

    def _do_put(self, packet: AbstractPacket, block: bool = True, timeout: float = None) -> None:
        """Overloaded method.

        See https://docs.python.org/3/library/queue.html as for the meaning
        of the function arguments.
        """
        queue.Queue.put(self, packet, block, timeout)

    def pop(self) -> Any:
        """Overloaded method.
        """
        return self.get()

    def size(self) -> int:
        """Overloaded method.
        """
        return self.qsize()

    def clear(self) -> None:
        """Overloaded method.
        """
        self.queue.clear()


class CircularBuffer(collections.deque, AbstractBuffer):

    """Implementation of a simple circular buffer.

    This is a simple subclass of the Python
    `collections.deque <https://docs.python.org/3/library/collections.html#collections.deque>`_
    data structure, adding I/O facilities on top of the base class.

    Verbatim from the Python documentation: `deques support thread-safe,
    memory efficient appends and pops from either side of the deque with
    approximately the same O(1) performance in either direction.`
    For completeness, the idea of using a deque to implement a circular buffer
    comes from https://stackoverflow.com/questions/4151320
    """

    def __init__(self, flush_size: int = None, flush_timeout: float = 10.) -> None:
        """Constructor.
        """
        collections.deque.__init__(self, [], None)
        AbstractBuffer.__init__(self, flush_size, flush_timeout)

    def _do_put(self, packet: AbstractPacket) -> None:
        """Overloaded method.
        """
        self.append(packet)

    def pop(self) -> Any:
        """Overloaded method.
        """
        return self.popleft()

    def size(self) -> int:
        """Overloaded method.
        """
        return len(self)

    def clear(self) -> None:
        """Overloaded method.
        """
        collections.deque.clear(self)
