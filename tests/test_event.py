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

from loguru import logger

from baldaquin import BALDAQUIN_DATA
from baldaquin.buf import CircularBuffer
from baldaquin.event import MockEvent, MockEventHandler
from baldaquin._qt import QtCore


def test_mock_event():
    """Create a mock event and make sure that pack() and unpack() roundtrip.
    """
    evt1 = MockEvent.random(0)
    logger.info(evt1)
    data = evt1.pack()
    logger.info(data)
    evt2 = MockEvent.unpack(data)
    logger.info(evt2)
    assert evt1.trigger_id == evt2.trigger_id
    assert evt1.seconds == evt2.seconds
    assert evt1.microseconds == evt2.microseconds
    assert evt1.pha == evt2.pha

def test_mock_event_io(num_events : int = 10):
    """Make sure that mock events can be written and read back from file.
    """
    file_path = os.path.join(BALDAQUIN_DATA, 'test_mock_event_io.bin')
    start_time = time.time()
    # Write random events to file...
    with open(file_path, 'wb') as output_file:
        for i in range(num_events):
            event = MockEvent.random(i, start_time)
            logger.info(event)
            output_file.write(event.pack())
    # ... and read them back.
    with open(file_path, 'rb') as input_file:
        for i in range(num_events):
            event = MockEvent.read_from_file(input_file)
            logger.info(event)
            assert event.trigger_id == i

def test_mock_event_buffer(num_events : int = 10):
    """Create an event buffer filled with mock events, and test the file I/O.
    """
    file_path = os.path.join(BALDAQUIN_DATA, 'test_mock_event_buffer.bin')
    start_time = time.time()
    # Create a circular buffer and fill it.
    buffer = CircularBuffer(file_path)
    for i in range(num_events):
        event = MockEvent.random(i, start_time)
        logger.info(event)
        buffer.put_item(event.pack())
    # Write the events to file...
    buffer.flush()
    # ... and read them back.
    with open(file_path, 'rb') as input_file:
        for i in range(num_events):
            event = MockEvent.read_from_file(input_file)
            logger.info(event)
            assert event.trigger_id == i

def test_mock_event_handler(rate=1000., write_interval=1., num_writes=5):
    """Small test function for the asynchronous event handler mechanism.
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