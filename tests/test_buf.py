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

"""Test suite for buf.py
"""

import os

import pytest

from baldaquin import BALDAQUIN_DATA
from baldaquin.buf import FIFO, CircularBuffer


def _test_buffer_base(buffer_class, num_items : int = 100, **kwargs):
    """Base function to test a generic, concrete subclass
    """
    file_path = os.path.join(BALDAQUIN_DATA, 'test_buffer.dat')
    buffer = buffer_class(**kwargs)
    for i in range(num_items):
        buffer.put(i)
    assert buffer.size() == num_items
    with pytest.raises(RuntimeError):
        buffer.flush()
    buffer.clear()

def test_fifo():
    """Test a FIFO
    """
    _test_buffer_base(FIFO)


def test_circular_buffer():
    """Test a circular buffer.
    """
    _test_buffer_base(CircularBuffer)
