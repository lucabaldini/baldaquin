# Copyright (C) 2023 the baldaquin team.
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

"""Test suite for xmaps.py
"""

from baldaquin import xmaps


def test_xmaps():
    """Basic test of some of the variables in xmaps.__init__
    """
    assert xmaps.XMAPS_BUFFER_FULL_MASK == 255
    assert xmaps.XMAPS_NUM_PIXELS == 1024
    assert xmaps.XMAPS_NUM_PIXELS_PER_BUFFER == 128
    assert xmaps.XMAPS_NUM_READOUT_CYCLES == 896
    assert xmaps.DacChannel.unused_channels() == (0, 1, 2, 3, 6)
