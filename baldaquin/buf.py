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

from loguru import logger

from baldaquin.profile import timing


class BufferWriteMode(enum.Enum):

    """Enum for the mode in which the output file is opened.
    """

    BINARY : str = 'b'
    TEXT: str = 't'



class BufferBase:

    """Base class for a data buffer.

    This is defining the three basic primitives, i.e., ``put_item()``, ``pop_item()``
    and ``num_items()``, and provides a working implementation of file I/O.

    Arguments
    ---------
    file_path : str
        The path to the output file.

    mode : BufferWriteMode
        The file write mode.
    """

    def __init__(self, file_path : str, mode : BufferWriteMode = BufferWriteMode.BINARY) -> None:
        """Constructor.
        """
        self.file_path = file_path
        self._mode = mode
        if os.path.exists(self.file_path):
            logger.warning(f'Output file {file_path} exists and will be overwritten')
        open(self.file_path, f'w{self._mode.value}').close()

    def put_item(self):
        """Put an item into the buffer (to be reimplemented in derived classes).
        """
        raise NotImplementedError

    def pop_item(self):
        """Pop an item from the buffer (to be reimplemented in derived classes).

        .. note::
            The specific semantic of `which` item is returned (e.g, the first,
            last, or something more clever) is delegated to the concrete classes,
            but we will be mostly dealing with FIFOs, i.e., unless otherwise
            stated it should be understood that this is popping items from the
            left of the queue.
        """
        raise NotImplementedError

    def num_items(self):
        """Return the number of items in the buffer (to be reimplemented in derived classes).
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
        num_items = self.num_items()
        if not num_items:
            return
        logger.debug(f'Writing {num_items} items to {self.file_path}...')
        total_size = 0
        with open(self.file_path, f'a{self._mode.value}') as output_file:
            for i in range(num_items):
                item = self.pop_item()
                total_size += len(item)
                output_file.write(item)
        logger.debug(f'Done, {total_size} Bytes written to disk.')



class FIFO(queue.Queue, BufferBase):

    """Implementation of a FIFO.

    This is using the `queue <https://docs.python.org/3/library/queue.html>`_
    module in the Python standard library.
    """

    def __init__(self, file_path : str, mode : BufferWriteMode = BufferWriteMode.BINARY,
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

    def put_item(self, item):
        """Overloaded method.
        """
        self.put(item)

    def pop_item(self):
        """Overloaded method.
        """
        return self.get()

    def num_items(self):
        """Overloaded method.
        """
        return self.qsize()



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

    def __init__(self, file_path : str, mode : BufferWriteMode = BufferWriteMode.BINARY,
                 max_size : int = None) -> None:
        """Constructor.
        """
        super().__init__([], max_size)
        BufferBase.__init__(self, file_path, mode)

    def put_item(self, item):
        """Overloaded method.
        """
        self.append(item)

    def pop_item(self):
        """Overloaded method.
        """
        return self.popleft()

    def num_items(self):
        """Overloaded method.
        """
        return len(self)
