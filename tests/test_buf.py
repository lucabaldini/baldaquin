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

import io
import os
import pytest

from baldaquin import logger, BALDAQUIN_DATA
from baldaquin.buf import FIFO, CircularBuffer, Sink
from baldaquin.pkt import Layout, Format, packetclass, FixedSizePacketBase


@packetclass
class Packet(FixedSizePacketBase):

    """Plausible data structure for testing purposes.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = 0xaa
    packet_id: Format.UNSIGNED_SHORT

    def as_text(self):
        """
        """
        return 'Packet\n'


def _test_buffer_base(buffer_class, num_packets: int = 10, **kwargs):
    """Base function to test a generic, concrete subclass
    """
    buffer = buffer_class(**kwargs)
    for i in range(num_packets):
        packet = Packet(Packet.header, i)
        buffer.put(packet)
    assert buffer.size() == num_packets
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


def test_sink_contextmanager():
    """Test the context manager sink protocol.
    """
    file_path = BALDAQUIN_DATA / 'sink.dat'
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    sink = Sink(file_path)
    with sink.open() as output_file:
        assert isinstance(output_file, io.IOBase)
    os.remove(file_path)


def test_buffer_flush(num_packets=10):
    """
    """
    buffer = CircularBuffer()
    file_path_b = BALDAQUIN_DATA / 'sink.dat'
    file_path_t = BALDAQUIN_DATA / 'sink.txt'
    try:
        os.remove(file_path_b)
    except FileNotFoundError:
        pass
    try:
        os.remove(file_path_t)
    except FileNotFoundError:
        pass

    buffer.add_sink(file_path_b)
    buffer.add_sink(file_path_t, 't', Packet.as_text)

    for i in range(num_packets):
        packet = Packet(Packet.header, i)
        buffer.put(packet)

    buffer.flush()
    #os.remove(file_path_b)
    #os.remove(file_path_t)
