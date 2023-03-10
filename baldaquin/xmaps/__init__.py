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

XMAPS is an array of 32 x 32 single-photon avalanche diodes (SPAD), for a total
of 1024 pixels with a built-in 7-bit counter. Additionally it features two peripheral
pixels for which we have access to the analog output.

The chip is divided in 8 logical buffer, each including 128 pixels, that are
readout in parallel. (That is, 128 pixels * 7 bits = 896 clock cycles are needed
for a full readout of the matrix.)

XMAPS comes with a 8-channels DAC to control the two peripheral pixels.
In the current implementation most of the channels of the DAC are actually
unused (i.e., disconnected), but it is good practice to set them to zero in
normal operation. The three used channels are:

* channel 4 (IBIAS): the bias current of the charge amplifier, in V. Note that
  3.3 V is off, and this should be the default value for operations not involving
  the peripheral analog pixels.
* channel 5 (IBR): the polarization voltage of the feedback network of the front-end.
  Defaults to 1.4 V.
* channel 7 (VTEST): the voltage level for the charge injection in the peripheral pixels.
"""

from enum import IntEnum


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



if __name__ == '__main__':
    # To be moved into a unit test.
    assert XMAPS_BUFFER_FULL_MASK == 255
    assert XMAPS_NUM_PIXELS == 1024
    assert XMAPS_NUM_PIXELS_PER_BUFFER == 128
    assert XMAPS_NUM_READOUT_CYCLES == 896
    assert DacChannel.unused_channels() == (0, 1, 2, 3, 6)
