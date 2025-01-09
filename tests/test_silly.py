# Copyright (C) 2024 the baldaquin team.
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

"""Unit tests for the silly apps.
"""


from baldaquin import logger
from baldaquin.silly.common import SillyPacket, SillyServer, SillyConfiguration



def test_packet():
    """Test the basic packet structure.
    """
    packet = SillyPacket(0, 1, 13080, 120)
    logger.info(packet)
    logger.info(packet.timestamp)


def test_server():
    """Test the event server.
    """
    server = SillyServer()
    for _ in range(5):
        data = server.next()
        logger.info(data)
        packet = SillyPacket.unpack(data)
        logger.info(packet)


def test_configuration():
    """Test for the server configuration.
    """
    config = SillyConfiguration()
    logger.info(config)
