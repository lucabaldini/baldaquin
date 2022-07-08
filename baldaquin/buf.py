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

from collections import deque
import os
from threading import Lock, Thread
import time

from loguru import logger

from baldaquin import BALDAQUIN_DATA


class DataBuffer(deque):

    """
    """

    def __init__(self, file_path : str, max_length : int = None):
        """
        """
        super().__init__([], max_length)
        self.file_path = file_path
        self._mutex = Lock()

    def append(self, item):
        """
        """
        #self._mutex.acquire()
        super().append(item)
        #self._mutex.release()

    def write(self):
        """
        """
        if not len(self):
            return
        #self._mutex.acquire()
        logger.debug(f'Writing {len(self)} packets to {self.file_path}...')
        with open(self.file_path, 'a') as output_file:
            while True:
                try:
                    output_file.write(f'{self.popleft()}\n')
                except IndexError:
                    break
        #self._mutex.release()


def _fill(buf):
    """
    """
    for i in range(100):
        buf.append(i)
        print(buf)
        time.sleep(0.1)

def _write(buf):
    """
    """
    while(1):
        buf.write()
        time.sleep(1.)


if __name__ == '__main__':
    file_path = os.path.join(BALDAQUIN_DATA, 'test.out')
    buf = DataBuffer(file_path, 100)
    print(buf)
    t1 = Thread(target=_fill, args=(buf,))
    t1.start()
    t2 = Thread(target=_write, args=(buf,))
    t2.start()
