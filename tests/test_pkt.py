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

from baldaquin import logger
from baldaquin.pkt import packetclass, AbstractPacket, FixedSizePacketBase, PacketStatistics
from baldaquin.pkt import Layout, Format, FieldMismatchError


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
    with pytest.raises(ValueError) as info:
        @packetclass
        class Packet(FixedSizePacketBase):
            layout = 'W'
    logger.info(info.value)

    with pytest.raises(ValueError) as info:
        @packetclass
        class Packet(FixedSizePacketBase):  # noqa: F811
            trigger_id: 'W'  # noqa: F821
    logger.info(info.value)

    with pytest.raises(FieldMismatchError) as info:
        _ = Readout(0, 0, 0)
    logger.info(info.value)


def test_readout():
    """Test a sensible packet structure.
    """
    # Test the class variables.
    assert Readout._fields == ('header', 'milliseconds', 'adc_value')
    assert Readout._format == '>BLH'
    assert Readout.size == 7

    # Create a class instance.
    packet = Readout(0xaa, 100, 127)
    assert isinstance(packet, AbstractPacket)
    logger.info(packet)
    # Test the post-initialization.
    assert packet.seconds == packet.milliseconds / 1000.
    # Make sure that pack/unpack do roundtrip.
    twin = Readout.unpack(packet.pack())
    logger.info(twin)
    for val1, val2 in zip(packet, twin):
        assert val1 == val2
    # Make sure that the packet fields cannot be modified.
    with pytest.raises(AttributeError) as info:
        packet.header = 3
    logger.info(info.value)


def test_docs():
    """Small convenience function for the class docs---we copy/paste from here.
    """

    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = Layout.BIG_ENDIAN

        header: Format.UNSIGNED_CHAR = 0xff
        pin_number: Format.UNSIGNED_CHAR
        timestamp: Format.UNSIGNED_LONG_LONG

    packet = Trigger(0xff, 1, 15426782)
    print(packet)
    print(len(packet))
    print(isinstance(packet, AbstractPacket))

    packet = Trigger.unpack(b'\xff\x01\x00\x00\x00\x00\x00\xebd\xde')
    print(packet)

    with pytest.raises(AttributeError) as info:
        packet.pin_number = 0
    print(info)

    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = Layout.BIG_ENDIAN

        header: Format.UNSIGNED_CHAR = 0xff
        pin_number: Format.UNSIGNED_CHAR
        microseconds: Format.UNSIGNED_LONG_LONG

        def __post_init__(self):
            self.seconds = self.microseconds / 1000000

    packet = Trigger(0xff, 1, 15426782)
    print(packet.seconds)


def test_text_output():
    """Test the text representation of the packet.
    """
    header = Readout.text_header()
    print(header)
    readout = Readout(0xaa, 2, 3)
    print(readout.to_text())


def test_packets_statistics():
    """Small test for the PacketStatistics class.
    """
    stats = PacketStatistics()
    logger.info(stats)
    stats.update(3, 3, 10)
    logger.info(stats)
