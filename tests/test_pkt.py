# Copyright (C) 2025 the baldaquin team.
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

"""Test suite for pkt.py
"""

import pytest

from baldaquin.env import BALDAQUIN_SCRATCH
from baldaquin.pkt import (
    AbstractPacket,
    FieldMismatchError,
    FixedSizePacketBase,
    Format,
    Layout,
    PacketFile,
    PacketStatistics,
    packetclass,
)


@packetclass
class Readout(FixedSizePacketBase):

    """Plausible data structure for testing purposes.
    """

    layout = Layout.BIG_ENDIAN
    header: Format.UNSIGNED_CHAR = 0xaa
    milliseconds: Format.UNSIGNED_LONG
    adc_value: Format.UNSIGNED_SHORT

    def __post_init__(self) -> None:
        self.seconds = self.milliseconds / 1000.


def test_format():
    """Test the check for the packet layout and format characters.
    """
    # pylint: disable=function-redefined, unused-variable
    with pytest.raises(ValueError):
        @packetclass
        class Packet(FixedSizePacketBase):
            layout = "W"

    with pytest.raises(ValueError):
        @packetclass
        class Packet(FixedSizePacketBase):  # noqa: F811
            trigger_id: "W"  # noqa: F821

    with pytest.raises(FieldMismatchError):
        _ = Readout(0, 0, 0)


def test_readout():
    """Test a sensible packet structure.
    """
    # pylint: disable=protected-access
    # Test the class variables.
    assert Readout._fields == ("header", "milliseconds", "adc_value")
    assert Readout._format == ">BLH"
    assert Readout.size == 7

    # Create a class instance.
    packet = Readout(0xaa, 100, 127)
    assert isinstance(packet, AbstractPacket)
    # Test the post-initialization.
    assert packet.seconds == packet.milliseconds / 1000.
    # Make sure that pack/unpack do roundtrip.
    twin = Readout.unpack(packet.pack())
    for val1, val2 in zip(packet, twin):
        assert val1 == val2
    # Make sure that the packet fields cannot be modified.
    with pytest.raises(AttributeError):
        packet.header = 3


def test_readout_subclass():
    """Test subclassing a concrete FixedSizePacketBase subclass.
    """

    @packetclass
    class SpecialReadout(Readout):

        board_number: Format.UNSIGNED_SHORT

    readout = SpecialReadout(0xaa, 100, 127, 3)
    assert readout.milliseconds == 100
    assert readout.adc_value == 127
    assert readout.board_number == 3


def test_text():
    """Test the join_attributes() method.
    """
    # pylint: disable=protected-access
    attrs = ("seconds", "adc_value")
    fmts = ("%.6f", "%d")
    packet = Readout(0xaa, 100, 127)
    assert packet._format_attributes(attrs, fmts) == ("0.100000", "127")
    assert packet._text(attrs, fmts, ", ") == "0.100000, 127\n"


def test_repr():
    """Test the terminal formatting helper function.
    """
    # pylint: disable=protected-access
    attrs = ("seconds", "adc_value")
    fmts = ("%.6f", "%d")
    packet = Readout(0xaa, 100, 127)
    assert packet._repr(attrs) == "Readout(seconds=0.1, adc_value=127)"
    assert packet._repr(attrs, fmts) == "Readout(seconds=0.100000, adc_value=127)"


def test_docs():
    """Small convenience function for the class docs---we copy/paste from here.
    """
    # pylint: disable=function-redefined
    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = Layout.BIG_ENDIAN

        header: Format.UNSIGNED_CHAR = 0xff
        pin_number: Format.UNSIGNED_CHAR
        timestamp: Format.UNSIGNED_LONG_LONG

    packet = Trigger(0xff, 1, 15426782)
    assert len(packet) == 10
    assert isinstance(packet, AbstractPacket)

    packet = Trigger.unpack(b"\xff\x01\x00\x00\x00\x00\x00\xebd\xde")

    with pytest.raises(AttributeError):
        packet.pin_number = 0

    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = Layout.BIG_ENDIAN

        header: Format.UNSIGNED_CHAR = 0xff
        pin_number: Format.UNSIGNED_CHAR
        microseconds: Format.UNSIGNED_LONG_LONG

        def __post_init__(self):
            self.seconds = self.microseconds / 1000000

    packet = Trigger(0xff, 1, 15426782)
    assert packet.seconds == 15.426782


def test_binary_io(num_packets: int = 10):
    """Write to and read from file in binary format.
    """
    file_path = BALDAQUIN_SCRATCH / "test_pkt.dat"
    with open(file_path, "wb") as output_file:
        for i in range(num_packets):
            output_file.write(Readout(0xaa, 1 * 1000, i + 100).data)
    with PacketFile(Readout).open(file_path) as input_file:
        for _ in input_file:
            pass
    with PacketFile(Readout).open(file_path) as input_file:
        packets = input_file.read_all()
        assert len(packets) == num_packets


def test_packets_statistics():
    """Small test for the PacketStatistics class.
    """
    stats = PacketStatistics()
    stats.update(3, 3, 10)
