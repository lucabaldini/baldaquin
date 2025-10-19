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

import contextlib

import pytest

from baldaquin import arduino_
from baldaquin.env import BALDAQUIN_SCRATCH
from baldaquin.serial_ import DeviceId

_UNO_IDS = ((0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043),
            (0x2341, 0x0243), (0x2341, 0x006A))


def test_concatenate_device_ids():
    """Test the board identiers.
    """
    assert arduino_.ArduinoBoard.concatenate_device_ids(arduino_.UNO) == _UNO_IDS


def test_board_retrieval():
    """Test the board identification code.
    """
    for device_id in _UNO_IDS:
        assert arduino_.ArduinoBoard.by_device_id(device_id) == arduino_.UNO
    assert arduino_.ArduinoBoard.by_designator("uno") == arduino_.UNO

    with pytest.raises(RuntimeError):
        arduino_.ArduinoBoard.by_device_id(DeviceId(-1, -1))

    with pytest.raises(RuntimeError):
        arduino_.ArduinoBoard.by_designator("una")


def test_autodetect():
    """Test the automatic detection of the Arduino board.
    """
    arduino_.autodetect_arduino_boards()
    arduino_.autodetect_arduino_boards(arduino_.UNO)
    arduino_.autodetect_arduino_board(arduino_.UNO)


def test_upload(test_data_path):
    """Test the sketch upload.

    Note this is within a try/except block because we cannot assume we have
    arduino-cli installed, nor a board attached to upload to.
    """
    file_path = test_data_path("blink", "blink_uno.hex")
    with contextlib.suppress(RuntimeError):
        arduino_.upload_sketch(file_path, "uno")


def test_compile(test_data_path):
    """Test the sketch compilation.

    Note this is within a try/except block because we cannot assume we have
    arduino-cli installed.
    """
    file_path = test_data_path("blink", "blink.ino")
    with contextlib.suppress(RuntimeError):
        arduino_.compile_sketch(file_path, "uno", BALDAQUIN_SCRATCH, verbose=False)


def test_project_name():
    """Test the project name machinery.
    """
    interface = arduino_.ArduinoProgrammingInterfaceBase
    for sketch_path in ("sketches/test/test.ino", "sketches/test/", "sketches/test"):
        assert interface.project_base_name(sketch_path) == "test"
        assert interface.project_name("sketches/test/test", "uno") == "test_uno"
