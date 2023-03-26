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

"""Test suite for timeline.py
"""

import numpy as np

from baldaquin.hist import Histogram1d, Histogram2d
from baldaquin.plt_ import plt

plt.ion()


def test_hist1d():
    """
    """
    plt.figure('Histogram 1d')
    binning = np.linspace(-5., 5., 100)
    h = Histogram1d(binning, xlabel='x').fill(np.random.normal(size=1000000))
    print(h.current_stats())
    h.plot()
    h.stat_box()



if __name__ == '__main__':
    test_hist1d()
    plt.show()
