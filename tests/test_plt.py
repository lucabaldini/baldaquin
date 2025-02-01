# Copyright (C) 2025 the baldaquin team.
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

"""Test suite the matplotlib stuff.
"""

import numpy as np

from baldaquin.plt_ import plt, VerticalCursor, setup_gca


def test_cursor():
    """Test the vertical cursor thing.
    """
    x = np.linspace(0., 2. * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    cursor = VerticalCursor()
    plt.plot(x, y1)
    cursor.add_data_set(x, y1)
    plt.plot(x, y2)
    cursor.add_data_set(x, y2)
    setup_gca(xmin=0., xmax=2. * np.pi, ymin=-1.25, ymax=1.25, grids=True)
    plt.gcf().canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
    return cursor


if __name__ == '__main__':
    # Note we have to keep a reference to the cursor not to loose it.
    cursor = test_cursor()
    plt.show()
