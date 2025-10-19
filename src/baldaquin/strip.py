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

import numpy as np

from .plt_ import plt, setup_axes


class SlidingStripChart:

    """Class describing a strip chart, that is, a scatter plot where the number of
    points is limited to a maximum, so that the thing acts essentially as a sliding
    window, typically in time.

    This is mainly meant to represent the time history of a signal over a reasonable
    span---a long-term acquisition might go on for weeks, and it would not make sense
    to try and plot on the screen millions of points, but the last segment of the
    acquisition is the most important part when we want to monitor what is happening.
    """

    # pylint: disable=invalid-name

    def __init__(self, max_length: int = None, label: str = '', xoffset: float = 0.,
                 xlabel: str = None, ylabel: str = None, datetime: bool = False) -> None:
        """Constructor.
        """
        self.label = label
        self.xoffset = xoffset
        self.xlabel = xlabel
        if self.xlabel is None and datetime:
            self.xlabel = 'UTC'
        self.ylabel = ylabel
        self.datetime = datetime
        self.x = collections.deque(maxlen=max_length)
        self.y = collections.deque(maxlen=max_length)

    def reset(self, max_length: int = None) -> None:
        """Reset the strip chart.
        """
        self.x = collections.deque(maxlen=max_length)
        self.y = collections.deque(maxlen=max_length)

    def add_point(self, x: float, y: float) -> None:
        """Append a data point to the strip chart.
        """
        self.x.append(x + self.xoffset)
        self.y.append(y)

    def plot(self, axes=None, **kwargs) -> None:
        """Plot the strip chart.
        """
        if axes is None:
            axes = plt.gca()
        x = np.array(self.x).astype('datetime64[s]') if self.datetime else self.x
        axes.plot(x, self.y, label=self.label, **kwargs)
        setup_axes(axes, xlabel=self.xlabel, ylabel=self.ylabel, grids=True)
