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

"""XMAPS basic layout.
"""

from enum import IntEnum
import os

from baldaquin import setup_project


XMAPS_PROJECT_NAME = 'xmaps'

XMAPS_CONFIG, XMAPS_APP_CONFIG, XMAPS_DATA = setup_project(XMAPS_PROJECT_NAME)

# Geometrical layout of the matrix.
XMAPS_NUM_COLS = 32
XMAPS_NUM_ROWS = 32
XMAPS_NUM_PIXELS = XMAPS_NUM_COLS * XMAPS_NUM_ROWS

# Redout buffers.
XMAPS_NUM_BUFFERS = 8
XMAPS_BUFFER_FULL_MASK = 2**XMAPS_NUM_BUFFERS - 1
XMAPS_NUM_PIXELS_PER_BUFFER = XMAPS_NUM_PIXELS // XMAPS_NUM_BUFFERS

# Depth of the pixel counters...
XMAPS_NUM_COUNTER_BITS = 7

# ... and total number of readout cycles for a full frame.
XMAPS_NUM_READOUT_CYCLES = XMAPS_NUM_COUNTER_BITS * XMAPS_NUM_PIXELS_PER_BUFFER


class DacChannel(IntEnum):

    """Layout of the multi-channel DAC for the control of the peripheral pixels.

    Note that we prepend an _ to the unused channels to flag them.
    """

    _CH0 = 0
    _CH1 = 1
    _CH2 = 2
    _CH3 = 3
    IBIAS = 4
    IBR = 5
    _CH6 = 6
    VTEST = 7

    @classmethod
    def unused_channels(cls, prefix : str = '_'):
        """Return the list of DAC channels that are unused---these are essentially
        all the channels whose names start with an underscore.
        """
        return tuple([ch.value for ch in cls if ch.name.startswith(prefix)])
