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
from pathlib import Path

import pytest

from baldaquin.buf import FIFO, CircularBuffer, Sink, WriteMode
from baldaquin.env import BALDAQUIN_DATA, BALDAQUIN_ENCODING
from baldaquin.pkt import FixedSizePacketBase, Format, Layout, packetclass


@packetclass
class Packet(FixedSizePacketBase):

    """Plausible data structure for testing purposes.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = 0xaa
    packet_id: Format.UNSIGNED_SHORT

    def as_text(self):
        """Simple text formatting function.
        """
        return f"{self.header}, {self.packet_id}\n"


def _test_buffer_base(buffer_class, num_packets: int = 10, **kwargs):
    """Base function to test a generic, concrete subclass
    """
    buffer = buffer_class(**kwargs)
    for i in range(num_packets):
        packet = Packet(Packet.header, i)
        buffer.put(packet)
    assert buffer.size() == num_packets
    # Since we have no sink connected, any flush attempt should raise an exception.
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


def _scrap_file(file_path: Path) -> Path:
    """Make sure that a given file does not exist, and remove if it does.
    """
    if file_path.exists():
        os.remove(file_path)
    return file_path


def test_sink_contextmanager():
    """Test the context manager sink protocol.
    """
    file_path = _scrap_file(BALDAQUIN_DATA / "sink.dat")
    # Create the sink.
    sink = Sink(file_path, WriteMode.BINARY)
    # Open the sink.
    with sink.open() as output_file:
        assert isinstance(output_file, io.IOBase)
    # Check that creating another sink with the same file path raises an exception.
    with pytest.raises(FileExistsError):
        sink = Sink(file_path, WriteMode.BINARY)
    # Cleanup.
    os.remove(file_path)


def test_sink_header():
    """Test the header for a text sink.
    """
    file_path = _scrap_file(BALDAQUIN_DATA / "sink.txt")
    header = "#This is a file header.\n"
    # Create the sink---this should write the header into the output file...
    _ = Sink(file_path, WriteMode.TEXT, header=header)
    # ... open the output file and make sure the content is correct.
    with open(file_path, encoding=BALDAQUIN_ENCODING) as input_file:
        assert input_file.read() == header
    # Cleanup.
    os.remove(file_path)


def test_buffer_flush(num_packets: int = 10):
    """Test the full flush mechanism with multiple sinks.
    """
    binary_file_path = _scrap_file(BALDAQUIN_DATA / "sink.dat")
    text_file_path = _scrap_file(BALDAQUIN_DATA / "sink.txt")
    # Create a buffer and assign two sinks.
    buffer = CircularBuffer()
    buffer.set_primary_sink(binary_file_path)
    buffer.add_custom_sink(text_file_path, WriteMode.TEXT, Packet.as_text, "#File header\n")
    # Fill the buffer with some packets.
    for i in range(num_packets):
        packet = Packet(Packet.header, i)
        buffer.put(packet)
    # At this point the buffer should have the target number of packets.
    assert buffer.size() == num_packets
    buffer.flush()
    # And now it should be empty.
    assert buffer.size() == 0
    with open(text_file_path, encoding=BALDAQUIN_ENCODING) as input_file:
        _ = input_file.read()
    # Cleanup
    os.remove(binary_file_path)
    os.remove(text_file_path)
