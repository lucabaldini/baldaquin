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

"""Test suite for arduino_.py
"""

from baldaquin import arduino_


_UNO_IDS = ((0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x2341, 0x0243), (0x2341, 0x006A))


def test_supported_boards():
    """List the supported boards.
    """
    for board in arduino_._SUPPORTED_BOARDS:
        print(board)

def test_board_identifiers():
    """Test the board identiers.
    """
    assert arduino_.board_identifiers(arduino_.UNO) == _UNO_IDS

def test_board_identify():
    """Test the board identification code.
    """
    for vid, pid in _UNO_IDS:
        assert arduino_.identify_arduino_board(vid, pid) == arduino_.UNO
