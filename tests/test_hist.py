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

from baldaquin.hist import Histogram1d
from baldaquin.plt_ import plt

_RNG = np.random.default_rng(313)


def test_hist1d(size=1000000, mean=10., sigma=2.):
    """A few tests for one-dimensional histograms.
    """
    binning = np.linspace(mean - 5. * sigma, mean + 5. * sigma, 100)
    x = _RNG.normal(mean, sigma, size)
    h = Histogram1d(binning, xlabel='x').fill(x)
    # Test that the histogram statistics is providing sensible values.
    # Note that the limits for the test, here, are purely heuristic---we should
    # probably do something more sensible from the statistcal point of view.
    hist_sumw, hist_mean, hist_rms = h.current_stats().values()
    assert abs((hist_sumw - size) / size) < 1.e-5
    assert abs(hist_mean - x.mean()) < 5.e-4
    assert abs(hist_rms - x.std()) < 5.e-3
    plt.figure('Histogram 1d')
    h.plot()
    h.stat_box()


if __name__ == '__main__':
    test_hist1d()
    plt.show()
