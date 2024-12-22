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

"""Strip-chart facilities.
"""

import collections

import matplotlib.dates

from baldaquin.plt_ import plt, setup_gca
from baldaquin.timeline import Timeline


class StripChart:

    """Class describing a strip chart, that is, a scatter plot where the number of
    points is limited to a maximum, so that the thing acts essentially as a sliding
    window, typically in time.

    This is mainly meant to represent the time history of a signal over a reasonable
    span---a long-term acquisition might go on for weeks, and it would not make sense
    to try and plot on the screen millions of points, but the last segment of the
    acquisition is the most important part when we want to monitor what is happening.
    """

    # pylint: disable=invalid-name

    def __init__(self, max_length: int, xoffset: float = 0., xlabel: str = None,
        ylabel: str = None) -> None:
        """Constructor.
        """
        self.xoffset = xoffset
        self.x = collections.deque(maxlen=max_length)
        self.y = collections.deque(maxlen=max_length)
        self.xlabel = xlabel
        self.ylabel = ylabel

    def append(self, x: float, y: float) -> None:
        """Append a data point to the strip chart.
        """
        self.x.append(x + self.xoffset)
        self.y.append(y)

    def plot(self, **kwargs) -> None:
        """Plot the strip chart.
        """
        #x = matplotlib.dates.num2date(np.array(self.x) / 86400)
        #plt.plot(x, self.y, **kwargs)
        plt.plot(self.x, self.y, **kwargs)
        setup_gca(xlabel=self.xlabel, ylabel=self.ylabel, grids=True)


if __name__ == '__main__':
    import numpy as np
    x = np.linspace(0., 1000., 100)
    y = np.sin(x / 100)
    timeline = Timeline()
    t0 = timeline.latch().seconds
    strip_chart = StripChart(50, t0)
    for _x, _y in zip(x, y):
        strip_chart.append(_x, _y)
    strip_chart.plot()
    plt.show()
