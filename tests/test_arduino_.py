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

import pytest

from baldaquin import logger, BALDAQUIN_DATA, BALDAQUIN_TEST_DATA
from baldaquin import arduino_
from baldaquin.serial_ import DeviceId


_UNO_IDS = ((0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043),
            (0x2341, 0x0243), (0x2341, 0x006A))


def test_supported_boards():
    """List the supported boards.
    """
    for board in arduino_._SUPPORTED_BOARDS:
        print(board)


def test_concatenate_device_ids():
    """Test the board identiers.
    """
    assert arduino_._concatenate_device_ids(arduino_.UNO) == _UNO_IDS


def test_board_retrieval():
    """Test the board identification code.
    """
    for device_id in _UNO_IDS:
        assert arduino_.board_by_device_id(device_id) == arduino_.UNO
    assert arduino_.board_by_designator('uno') == arduino_.UNO

    with pytest.raises(RuntimeError) as info:
        arduino_.board_by_device_id(DeviceId(-1, -1))
    logger.info(info)

    with pytest.raises(RuntimeError) as info:
        arduino_.board_by_designator('una')
    logger.info(info)


def test_compile():
    """
    """
    file_path = BALDAQUIN_TEST_DATA / 'blink' / 'blink.ino'
    arduino_.compile_sketch(file_path, BALDAQUIN_DATA, 'uno', verbose=False)
