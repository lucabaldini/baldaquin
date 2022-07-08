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

import random
import sys
import time
from typing import Any

from loguru import logger

from baldaquin.buf import CircularBuffer
from baldaquin._qt import QtCore



class EventHandlerBase(QtCore.QRunnable):

    """Base class for an event handler.
    """

    def __init__(self, file_path : str, max_length : int = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.buffer = CircularBuffer(file_path, max_length)
        self.__running = False

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def run(self) -> None:
        """Overloaded QRunnable method.
        """
        self.__running = True
        while self.__running:
            self.buffer.append(self.process_event())

    def write(self):
        """Write data to file.
        """
        self.buffer.write()

    def process_event(self) -> Any:
        """Process a single event.

        This must be overloaded in derived functions.
        """
        raise NotImplementedError



class MockEventHandler(EventHandlerBase):

    """Mock event handler for testing purposes.
    """

    def __init__(self, file_path : str, max_length : int = None, rate : float = 10.):
        """Constructor.
        """
        super().__init__(file_path, max_length)
        self._rate = rate
        self._trigger_id = 0
        self._timestamp = 0.

    def process_event(self) -> Any:
        """Overloaded method.
        """
        dt = random.expovariate(self._rate)
        self._trigger_id += 1
        self._timestamp += dt
        time.sleep(dt)
        return (self._trigger_id, self._timestamp)



def test(rate=1000., write_interval=1., num_writes=5):
    """Small test functions
    """
    import os
    from baldaquin import BALDAQUIN_DATA
    file_path = os.path.join(BALDAQUIN_DATA, 'test.out')
    evt = MockEventHandler(file_path, rate=rate)
    evt.buffer.create_file()
    pool = QtCore.QThreadPool.globalInstance()
    pool.start(evt)
    for i in range(num_writes):
        time.sleep(write_interval)
        evt.write()
    evt.stop()
    pool.waitForDone()
    evt.write()
    assert len(evt.buffer) == 0



if __name__ == '__main__':
    test()
