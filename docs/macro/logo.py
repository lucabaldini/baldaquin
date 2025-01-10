# Copyright (C) 2022 the baldaquin team.
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

"""The glorious baldaquin logo :-)
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from baldaquin import BALDAQUIN_DOCS_STATIC

FIG_SIDE = 6
MODES = ('light', 'dark')
FILL_COLOR = 'skyblue'


def _line_color(mode):
    """Get the line color for the theme.
    """
    assert mode in MODES
    if mode == 'light':
        return 'lightgray'
    if mode == 'dark':
        return 'white'


def plot_spline(*nodes, control_points=False, **kwargs):
    """Generic function to plot a spline.
    """
    xp = np.array(nodes)[:, 0]
    yp = np.array(nodes)[:, 1]
    tck, u = interpolate.splprep([xp, yp], s=0)
    x, y = interpolate.splev(np.linspace(0., 1., 100), tck, der=0)
    plt.plot(x, y, **kwargs)
    if control_points:
        plt.plot(xp, yp, 'o')
    return x, y


def figure(x1=-1.1, x2=1.1, y1=-1.1, y2=1.1):
    """Crete the logo figure.
    """
    plt.figure(figsize=(FIG_SIDE, FIG_SIDE))
    plt.gca().set_aspect('equal')
    plt.gca().axis((x1, x2, y1, y2))
    plt.subplots_adjust(left=0., right=1., bottom=0., top=1.)
    plt.axis('off')


def plot_baldaquin(line_color, lw, w=0.425, h=0.40, wave=True):
    """Plot the glorious baldaquin.
    """
    kwargs = dict(color=line_color, lw=lw)
    plt.plot((-w, -w, w, w), (-h, h, h, -h), **kwargs)
    x, y = plot_spline((0., 0.99 * h), (-0.05 * w, 0.8 * h),
                       (-0.4 * w, 0.5 * h), (-w, 0.), **kwargs)
    plt.fill_between(x, y, np.full(x.shape, h), color=FILL_COLOR)
    x, y = plot_spline((0., 0.99 * h), (0.05 * w, 0.8 * h), (0.4 * w, 0.5 * h), (w, 0.), **kwargs)
    plt.fill_between(x, y, np.full(x.shape, h), color=FILL_COLOR)
    plot_spline((-1.25 * w, 0.9 * h), (-w, h), (-0.5 * w, 1.25 * h), (0., 1.75 * h), **kwargs)
    plot_spline((1.25 * w, 0.9 * h), (w, h), (0.5 * w, 1.25 * h), (0., 1.75 * h), **kwargs)
    if wave:
        x = np.linspace(-0.8 * w, 0.8 * w, 100)
        y = -1.25 * h + 0.25 * h * np.cos(30 * x) * np.exp(-3. * x)
        plt.plot(x, y, color=line_color, lw=lw)


def create_logo(mode, lw=3.5, circle_radius=1.):
    """Create the big logo.
    """
    line_color = _line_color(mode)
    figure()
    circle = plt.Circle((0, 0), circle_radius, color=line_color, lw=3.5, fill=False)
    plt.gca().add_patch(circle)
    plt.text(0., 0., 'bal  daq  uin', ha='center', va='center', size=60, color=FILL_COLOR)
    plot_baldaquin(line_color, lw)
    text = 'BALd DAQ User INterface'
    max_angle = np.radians(55.)
    num_letters = len(text)
    radius = 0.925 * circle_radius
    for i, letter in enumerate(text):
        angle = -max_angle + 2. * max_angle * (i / (num_letters - 1)) - 0.5 * np.pi
        x, y = radius * np.cos(angle), radius * np.sin(angle)
        plt.text(x, y, letter, size=20., rotation=np.degrees(angle) + 90., ha='center',
                 va='center', color=FILL_COLOR)
    file_name = f'baldaquin_logo_{mode}.png'
    plt.savefig(os.path.join(BALDAQUIN_DOCS_STATIC, file_name), transparent=True)


def create_small_logo(mode, lw=15.):
    """Create the small logo.
    """
    line_color = _line_color(mode)
    figure(-0.54, 0.54, -0.36, 0.72)
    plot_baldaquin(line_color=line_color, lw=lw, wave=False)
    file_name = f'baldaquin_logo_small_{mode}.png'
    plt.savefig(os.path.join(BALDAQUIN_DOCS_STATIC, file_name), transparent=True)


for mode in MODES:
    create_logo(mode)
    create_small_logo(mode)


plt.show()
