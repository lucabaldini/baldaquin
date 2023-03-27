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

import collections
import enum
import os
from pathlib import Path
import queue
import time
from typing import Any

from loguru import logger

from baldaquin.profile import timing


class BufferWriteMode(enum.Enum):

    """Enum for the mode in which the output file is opened.
    """

    BINARY : str = 'b'
    TEXT: str = 't'



class BufferBase:

    """Base class for a data buffer.

    Arguments
    ---------
    max_size : int
        The maximum number of events the buffer can physically contain.

    flush_size : int
        The maximum number of events before a
        :meth:`flush_needed() <baldaquin.buf.BufferBase.flush_needed()>`
        call returns True (mind this should be smaller than ``max_size`` because
        otherwise the buffer will generally drop events).

    flush_interval : float
        The maximum time (in s) elapsed since the last
        :meth:`flush() <baldaquin.buf.BufferBase.flush()>` before a
        :meth:`flush_needed() <baldaquin.buf.BufferBase.flush_needed()>` call
        returns True.

    mode : BufferWriteMode
        The file write mode.
    """

    _DEFAULT_ENCODING = 'utf-8'

    def __init__(self, max_size : int, flush_size : int, flush_interval : float,
        mode : BufferWriteMode) -> None:
        """Constructor.
        """
        if max_size is not None and flush_size is not None and max_size <= flush_size:
            raise RuntimeError(f'Buffer physical size ({max_size}) <= flush size ({flush_size})')
        self._max_size = max_size
        self._flush_size = flush_size
        self._flush_interval = flush_interval
        self._mode = mode
        self._last_flush_time = time.time()
        self._current_file_path = None

    def _file_open_kwargs(self):
        """Return the proper keyword arguments (mode and encoding) for a generic
        open() call.
        """
        kwargs = dict(mode=f'w{self._mode.value}')
        if self._mode == BufferWriteMode.TEXT:
            kwargs.update(encoding=self._DEFAULT_ENCODING)
        return kwargs

    def set_output_file(self, file_path : Path) -> None:
        """Set the output file for flushing the buffer.
        """
        # If we're targeting the current file path, then there is nothing to do.
        if file_path == self._current_file_path:
            return
        # If the target file path is None, then we're disconnecting from the
        # current file.
        if file_path is None:
            logger.info(f'Disconnecting the event buffer from {self._current_file_path}...')
            self._current_file_path = None
            return
        # Otherwise we're actually opening a new file and getting it ready.
        self._current_file_path = file_path
        logger.info(f'Directing the event buffer to {self._current_file_path}...')
        if os.path.exists(self._current_file_path):
            logger.warning(f'Output file {self._current_file_path} exists and will be overwritten')
        # pylint: disable=consider-using-with, unspecified-encoding
        open(self._current_file_path, **self._file_open_kwargs()).close()

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

    @timing
    def flush(self) -> tuple[int, int]:
        """Write the content of the buffer to file and returns the number of
        objects written to disk.

        .. note::
           This will write all the items in the buffer at the time of the
           function call, i.e., items added while writing to disk will need to
           wait for the next call.
        """
        # If there is no output file path set, then something went horribly wrong...
        if self._current_file_path is None:
            raise RuntimeError('Output file not set, cannot flush buffer.')
        # Cache the number of events to be read---this is implemented this way
        # as we might be adding new events while flushing the buffer.
        num_events = self.size()
        num_bytes = 0
        self._last_flush_time = time.time()
        # If there are no events, then there is nothing to do, and we are not
        # actually flushing the buffer.
        if num_events == 0:
            return (num_events, num_bytes)
        # And, finally, the actual thing.
        logger.info(f'Writing {num_events} events to {self._current_file_path}...')
        # pylint: disable=unspecified-encoding
        with open(self._current_file_path, **self._file_open_kwargs()) as output_file:
            for _ in range(num_events):
                item = self.pop()
                num_bytes += len(item)
                output_file.write(item)
        logger.info(f'Done, {num_bytes} Bytes written to disk.')
        return (num_events, num_bytes)

    def put(self, item : Any) -> None:
        """Put an item into the buffer (to be reimplemented in derived classes).
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



class FIFO(queue.Queue, BufferBase):

    """Implementation of a FIFO.

    This is using the `queue <https://docs.python.org/3/library/queue.html>`_
    module in the Python standard library.

    Note that the queue.Queue class is internally using a collections.deque
    object, so this is effectively another layer of complexity over the
    CircularBuffer class below. It's not entirely clear to me what the real
    difference would be, in a multi-threaded context.
    """

    def __init__(self, max_size : int = None, flush_size : int = None,
        flush_interval : float = 1., mode : BufferWriteMode = BufferWriteMode.BINARY) -> None:
        """Constructor.
        """
        # From the stdlib documentation: maxsize is an integer that sets the
        # upperbound limit on the number of items that can be placed in the queue.
        # If maxsize is less than or equal to zero, the queue size is infinite.
        if max_size is None:
            max_size = -1
        queue.Queue.__init__(self, max_size)
        BufferBase.__init__(self, max_size, flush_size, flush_interval, mode)

    def put(self, item : Any, block : bool = True, timeout : float = None) -> None:
        """Overloaded method.

        See https://docs.python.org/3/library/queue.html as for the meaning
        o the function arguments.
        """
        queue.Queue.put(self, item, block, timeout)

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

    def __init__(self, max_size : int = None, flush_interval : float = 1.,
        flush_size : int = None, mode : BufferWriteMode = BufferWriteMode.BINARY) -> None:
        """Constructor.
        """
        collections.deque.__init__(self, [], max_size)
        BufferBase.__init__(self, max_size, flush_size, flush_interval, mode)

    def put(self, item : Any) -> None:
        """Overloaded method.
        """
        self.append(item)

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
