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

from loguru import logger

from baldaquin._gui import QtCore


class DataBuffer(deque):

    """
    """

    def __init__(self, file_path : str, max_length : int = None):
        """
        """
        super().__init__([], max_length)
        self.file_path = file_path
        self._mutex = QtCore.QMutex()
        self._timer = QtCore.QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(lambda item=self: item.write)
        self._timer.start()

    def append(self, item):
        """
        """
        self._mutex.lock()
        super().append(item)
        self._mutex.unlock()

    def write(self):
        """
        """
        print(len(self))
        if not len(self):
            return
        self._mutex.lock()
        logger.debug(f'Writing {len(self)} packets to {self.file_path}...')
        with open(file_path, 'a') as output_file:
            for item in self:
                output_file.write(item)
        self._mutex.unlock()




if __name__ == '__main__':
    from baldaquin import BALDAQUIN_DATA
    import os
    import time
    file_path = os.path.join(BALDAQUIN_DATA, 'test.out')
    buf = DataBuffer(file_path, 3)
    for i in range(1000):
        buf.append(i)
        print(buf)
        time.sleep(0.1)
    print(buf)
