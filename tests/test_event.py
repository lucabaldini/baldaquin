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

"""Test suite for event.py
"""

import os
import time

from baldaquin import BALDAQUIN_DATA
from baldaquin.event import MockEventHandler
from baldaquin._qt import QtCore


def test_mock_event_handler(rate=1000., write_interval=1., num_writes=5):
    """Small test function for the event handler mechanism.
    """
    file_path = os.path.join(BALDAQUIN_DATA, 'test.out')
    evt_handler = MockEventHandler(file_path, rate=rate)
    pool = QtCore.QThreadPool.globalInstance()
    pool.start(evt_handler)
    for i in range(num_writes):
        time.sleep(write_interval)
        evt_handler.buffer.flush()
    evt_handler.stop()
    pool.waitForDone()
    evt_handler.buffer.flush()
    assert evt_handler.buffer.num_items() == 0
