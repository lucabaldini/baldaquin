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

"""Data buffering.
"""

import collections
import enum
import os
import queue
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

    This is defining the three basic primitives, i.e., ``put()``, ``pop()``
    and ``size()``, and provides a working implementation of file I/O.

    Arguments
    ---------
    file_path : str
        The path to the output file.

    mode : BufferWriteMode
        The file write mode.
    """

    def __init__(self, file_path : str = None, mode : BufferWriteMode = BufferWriteMode.BINARY) -> None:
        """Constructor.
        """
        self.file_path = None
        self._mode = mode
        if file_path is not None:
            self.set_output_file(file_path)

    def set_output_file(self, file_path):
        """Set the output file for flushing the buffer.
        """
        self.file_path = file_path
        if os.path.exists(self.file_path):
            logger.warning(f'Output file {self.file_path} exists and will be overwritten')
        # pylint: disable=consider-using-with
        open(self.file_path, f'w{self._mode.value}').close()

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

    @timing
    def flush(self) -> None:
        """Write the content of the buffer to file and returns the number of
        objects written to disk.

        .. note::
           This will write all the items in the buffer at the time of the
           function call, i.e., items added while writing to disk will need to
           wait for the next call.
        """
        if self.file_path is None:
            raise RuntimeError('Output file not set, cannot flush buffer.')
        size = self.size()
        if not size:
            return
        logger.info(f'Writing {size} items to {self.file_path}...')
        total_size = 0
        with open(self.file_path, f'a{self._mode.value}') as output_file:
            for _ in range(size):
                item = self.pop()
                total_size += len(item)
                output_file.write(item)
        logger.info(f'Done, {total_size} Bytes written to disk.')



class FIFO(queue.Queue, BufferBase):

    """Implementation of a FIFO.

    This is using the `queue <https://docs.python.org/3/library/queue.html>`_
    module in the Python standard library.

    Note that the queue.Queue class is internally using a collections.deque
    object, so this is effectively another layer of complexity over the
    CircularBuffer class below. It's not entirely clear to me what the real
    difference would be, in a multi-threaded context.
    """

    def __init__(self, file_path : str = None, mode : BufferWriteMode = BufferWriteMode.BINARY,
                 max_size : int = None) -> None:
        """Constructor.
        """
        # From the stdlib documentation: maxsize is an integer that sets the
        # upperbound limit on the number of items that can be placed in the queue.
        # If maxsize is less than or equal to zero, the queue size is infinite.
        if max_size is None:
            max_size = -1
        super().__init__(max_size)
        BufferBase.__init__(self, file_path, mode)

    def put(self, item : Any) -> None:
        """Overloaded method.
        """
        queue.Queue.put(self, item)

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

    def __init__(self, file_path : str = None, mode : BufferWriteMode = BufferWriteMode.BINARY,
                 max_size : int = None) -> None:
        """Constructor.
        """
        super().__init__([], max_size)
        BufferBase.__init__(self, file_path, mode)

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
