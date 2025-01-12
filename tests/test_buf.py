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


import pytest

from baldaquin.buf import FIFO, CircularBuffer, Sink
from baldaquin.pkt import Layout, Format, packetclass, FixedSizePacketBase


@packetclass
class Packet(FixedSizePacketBase):

    """Plausible data structure for testing purposes.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = 0xaa
    packet_id: Format.UNSIGNED_SHORT


def _test_buffer_base(buffer_class, num_items: int = 10, **kwargs):
    """Base function to test a generic, concrete subclass
    """
    buffer = buffer_class(**kwargs)
    for i in range(num_items):
        packet = Packet(Packet.header, i)
        buffer.put(packet)
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


def test_sinks():
    """
    """
