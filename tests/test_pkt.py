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

from dataclasses import dataclass

import pytest

from baldaquin import logger
from baldaquin import BALDAQUIN_DATA
from baldaquin.pkt import packetclass, AbstractPacket, FixedSizePacketBase, PacketStatistics
from baldaquin.pkt import LayoutCharacterError, FormatCharacterError, FieldMismatchError


@packetclass
class Readout(FixedSizePacketBase):

    """Plausible data structure for testing purposes.
    """

    layout = '>'
    header: 'B' = 0xaa
    milliseconds: 'L'
    adc_value: 'H'

    def __post_init__(self) -> None:
        self.seconds = self.milliseconds / 1000.



def test_format():
    """Test the check for the packet layout and format characters.
    """
    with pytest.raises(LayoutCharacterError) as info:
        @packetclass
        class Packet(FixedSizePacketBase):
            layout = 'W'
    logger.info(info.value)

    with pytest.raises(FormatCharacterError) as info:
        @packetclass
        class Packet(FixedSizePacketBase):
            trigger_id: 'W'
    logger.info(info.value)

    with pytest.raises(FieldMismatchError) as info:
        packet = Readout(0, 0, 0)
    logger.info(info.value)


def test_readout():
    """Test a sensible packet structure.
    """
    # Test the class variables.
    assert Readout._fields == ('header', 'milliseconds', 'adc_value')
    assert Readout._format == '>BLH'
    assert Readout._size == 7
    # Create a class instance.
    packet = Readout(0xaa, 100, 127)
    assert isinstance(packet, AbstractPacket)
    logger.info(packet)
    # Test the post-initialization.
    assert packet.seconds == packet.milliseconds / 1000.

    #packet.header = 3

    # Make sure that pack/unpack do roundtrip.
    twin = Readout.unpack(packet.pack())
    logger.info(twin)
    for val1, val2 in zip(packet, twin):
        assert val1 == val2


def test_packets_statistics():
    """Small test for the PacketStatistics class.
    """
    stats = PacketStatistics()
    logger.info(stats)
    stats.update(3, 3, 10)
    logger.info(stats)
