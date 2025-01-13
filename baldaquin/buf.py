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
from collections.abc import Callable
from contextlib import contextmanager
from enum import Enum
import io
from pathlib import Path
import queue
import time
from typing import Any

from baldaquin import logger, DEFAULT_CHARACTER_ENCODING
from baldaquin.pkt import AbstractPacket
from baldaquin.profile import timing


class WriteMode(Enum):

    """Small enum class for the file write mode.

    Note this has to match the open modes in the Python open() builtin.
    """

    BINARY = 'b'
    TEXT = 't'


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
            raise FileExistsError(f'Output file {file_path} already exists')
        self.file_path = file_path
        self.formatter = formatter
        self._mode = mode
        self._output_file = None
        # Note we always open the output file in append mode.
        self._open_kwargs = dict(mode=f'a{self._mode.value}')
        if self._mode == WriteMode.TEXT:
            self._open_kwargs.update(encoding=DEFAULT_CHARACTER_ENCODING)
        # At this point we do create the file and, if needed, we write the
        # header into it. (And we are ready to flush.)
        with self.open() as output_file:
            if header is not None:
                logger.debug('Writing file header...')
                output_file.write(header)

    @contextmanager
    def open(self) -> io.IOBase:
        """Open the proper file object and return it.

        Note this is implemented as a context manager, and yields a reference to
        the underlying (open) output file.
        """
        # pylint: disable=unspecified-encoding
        logger.debug(f'Opening output file {self.file_path} {self._open_kwargs}...')
        output_file = open(self.file_path, **self._open_kwargs)
        yield output_file
        output_file.close()
        logger.debug(f'Ouput file {self.file_path} closed.')

    def __str__(self) -> str:
        """String formatting.
        """
        if self.formatter is None:
            return f'Sink -> {self.file_path} ({self._mode})'
        return f'Sink -> {self.file_path} ({self._mode}, {self.formatter.__qualname__})'


class BufferBase:

    """Base class for a data buffer.

    Arguments
    ---------
    max_size : int
        The maximum number of packets the buffer can physically contain.

    flush_size : int
        The maximum number of packets before a
        :meth:`flush_needed() <baldaquin.buf.BufferBase.flush_needed()>`
        call returns True (mind this should be smaller than ``max_size`` because
        otherwise the buffer will generally drop packets).

    flush_interval : float
        The maximum time (in s) elapsed since the last
        :meth:`flush() <baldaquin.buf.BufferBase.flush()>` before a
        :meth:`flush_needed() <baldaquin.buf.BufferBase.flush_needed()>` call
        returns True.

    mode : str
        The file write mode.
    """

    def __init__(self, max_size: int, flush_size: int, flush_interval: float, mode: str) -> None:
        """Constructor.
        """
        if max_size is not None and flush_size is not None and max_size <= flush_size:
            raise RuntimeError(f'Buffer physical size ({max_size}) <= flush size ({flush_size})')
        self._max_size = max_size
        self._flush_size = flush_size
        self._flush_interval = flush_interval
        self._mode = mode
        self._last_flush_time = time.time()
        self._sinks = []
        # To be removed.
        self._current_file_path = None

    def put(self, packet: AbstractPacket) -> None:
        """Put an item into the buffer (to be reimplemented in derived classes).
        """
        if not isinstance(packet, AbstractPacket):
            raise TypeError(f'{packet} is not an AbstractPacket instance')
        self._do_put(packet)

    def _do_put(self, packet: AbstractPacket) -> None:
        """
        """
        raise NotImplementedError

    def pop(self) -> Any:
        """Pop an item from the buffer (to be reimplemented in derived classes).

        .. note::
            The specific semantic of `which` item is returned (e.g, the first,
            last, or something more clever) is delegated to the concrete classes,
            but we will be mostly dealing with FIFOs, i.e., unless otherwise
            stated it should be understood that this is popping items from the
            left of the queue.
        """
        raise NotImplementedError

    def size(self) -> int:
        """Return the number of items in the buffer (to be reimplemented in derived classes).
        """
        raise NotImplementedError

    def clear(self) -> None:
        """Clear the buffer.
        """
        raise NotImplementedError

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
        if self.almost_full() or self.time_since_last_flush() > self._flush_interval:
            return True
        return False

    def add_sink(self, file_path: Path, mode: WriteMode, formatter: Callable = None,
                 header=None) -> None:
        """Add a sink to the buffer.
        """
        if len(self._sinks) == 0 and formatter is not None:
            raise RuntimeError('The first sink connected to a buffer has non trivial flush')
        sink = Sink(file_path, mode, formatter, header)
        logger.info(f'Connecting buffer to {sink}...')
        self._sinks.append(sink)

    def disconnect(self) -> None:
        """Disconnect all sinks.
        """
        self._sinks = []
        logger.info('All buffer sinks disconnected.')

    # def set_output_file(self, file_path: Path) -> None:

    def _write_native(self, num_packets: int, output_file) -> int:
        """
        """
        num_bytes_written = 0
        for _ in range(num_packets):
            num_bytes_written += output_file.write(self.pop().payload)
        logger.debug(f'{num_bytes_written} bytes written to file.')
        return num_bytes_written

    def _write_custom(self, num_packets: int, output_file, formatter) -> int:
        """
        """
        num_bytes_written = 0
        for i in range(num_packets):
            num_bytes_written += output_file.write(formatter(self[i]))
        logger.debug(f'{num_bytes_written} bytes written to file.')
        return num_bytes_written

    @timing
    def flush(self) -> tuple[int, int]:
        """Write the content of the buffer to file and returns the number of
        objects written to disk.

        .. note::
           This will write all the items in the buffer at the time of the
           function call, i.e., items added while writing to disk will need to
           wait for the next call.
        """
        if len(self._sinks) == 0:
            raise RuntimeError('No sink connected to the buffer, cannot flush')
        # Cache the number of packets to be read---this is implemented this way
        # as we might be adding new packets while flushing the buffer.
        num_packets = self.size()
        num_bytes = 0
        self._last_flush_time = time.time()
        # If there are no packets, then there is nothing to do, and we are not
        # actually flushing the buffer.
        if num_packets == 0:
            return (num_packets, num_bytes)
        # And, finally, the actual flush.
        logger.info(f'{num_packets} packets ready to be written out...')
        for i, sink in enumerate(reversed(self._sinks)):
            with sink.open() as output_file:
                if i != len(self._sinks) - 1:
                    self._write_custom(num_packets, output_file, sink.formatter)
                else:
                    self._write_native(num_packets, output_file)
        logger.info(f'{num_bytes} bytes written to disk.')
        return (num_packets, num_bytes)


class FIFO(queue.Queue, BufferBase):

    """Implementation of a FIFO.

    This is using the `queue <https://docs.python.org/3/library/queue.html>`_
    module in the Python standard library.

    Note that the queue.Queue class is internally using a collections.deque
    object, so this is effectively another layer of complexity over the
    CircularBuffer class below. It's not entirely clear to me what the real
    difference would be, in a multi-threaded context.
    """

    def __init__(self, max_size: int = None, flush_size: int = None, flush_interval: float = 1.,
                 mode: str = 'b') -> None:
        """Constructor.
        """
        # From the stdlib documentation: maxsize is an integer that sets the
        # upperbound limit on the number of items that can be placed in the queue.
        # If maxsize is less than or equal to zero, the queue size is infinite.
        if max_size is None:
            max_size = -1
        queue.Queue.__init__(self, max_size)
        BufferBase.__init__(self, max_size, flush_size, flush_interval, mode)

    def _do_put(self, packet: AbstractPacket, block: bool = True, timeout: float = None) -> None:
        """Overloaded method.

        See https://docs.python.org/3/library/queue.html as for the meaning
        o the function arguments.
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


class CircularBuffer(collections.deque, BufferBase):

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

    def __init__(self, max_size: int = None, flush_interval: float = 1.,
                 flush_size: int = None, mode: str = 'b') -> None:
        """Constructor.
        """
        collections.deque.__init__(self, [], max_size)
        BufferBase.__init__(self, max_size, flush_size, flush_interval, mode)

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
