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

import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

FIG_SIDE = 6
COLOR_1 = 'lightgray'
COLOR_2 = 'skyblue'
LINE_WIDTH = 3.5
CIRCLE_RADIUS = 1.


def plot_spline(*nodes, color=COLOR_1, lw=LINE_WIDTH, control_points=False):
    """Generic function to plot a spline.
    """
    x = np.array(nodes)[:,0]
    y = np.array(nodes)[:,1]
    tck, u = interpolate.splprep( [x,y] ,s = 0 )
    xnew, ynew = interpolate.splev( np.linspace( 0, 1, 100 ), tck,der = 0)
    plt.plot(xnew, ynew, color=color, lw=lw)
    if control_points:
        plt.plot(x, y, 'o')
    return xnew, ynew

def plot_baldaquin(w = 0.425, h = 0.40, line_color=COLOR_1, fill_color=COLOR_2,
    lw=LINE_WIDTH, wave=True):
    """
    """
    kwargs = dict(color=line_color, lw=lw)
    plt.plot((-w, -w, w, w), (-h, h, h, -h), **kwargs)
    x, y = plot_spline((0., 0.99 * h), (-0.05 * w, 0.8 * h), (-0.4 * w, 0.5 * h), (-w, 0.), **kwargs)
    plt.fill_between(x, y, np.full(x.shape, h), color=fill_color)
    x, y = plot_spline((0., 0.99 * h), (0.05 * w, 0.8 * h), (0.4 * w, 0.5 * h), (w, 0.), **kwargs)
    plt.fill_between(x, y, np.full(x.shape, h), color=fill_color)
    plot_spline((-1.25 * w, 0.9 * h), (-w, h), (-0.5 * w, 1.25 * h), (0., 1.75 * h), **kwargs)
    plot_spline((1.25 * w, 0.9 * h), (w, h), (0.5 * w, 1.25 * h), (0., 1.75 * h), **kwargs)
    if wave:
        x = np.linspace(-0.8 * w, 0.8 * w, 100)
        y = -1.25 * h + 0.25 * h * np.cos(30 * x) * np.exp(-3. * x)
        plt.plot(x, y, color=line_color, lw=LINE_WIDTH)

def figure(x1=-1.1, x2=1.1, y1=-1.1, y2=1.1, background_color='white'):
    """
    """
    plt.figure(figsize=(FIG_SIDE, FIG_SIDE), facecolor=background_color)
    plt.gca().set_aspect('equal')
    plt.gca().axis((x1, x2, y1, y2))
    plt.subplots_adjust(left=0., right=1., bottom=0., top=1.)
    plt.axis('off')


figure()
circle = plt.Circle((0, 0), CIRCLE_RADIUS, color=COLOR_1, lw=LINE_WIDTH, fill=False)
plt.gca().add_patch(circle)
plt.text(0., 0., 'bal  daq  uin', ha='center', va='center', size=60, color=COLOR_2)
plot_baldaquin()
text = 'BALanced DAQ User INterface'
max_angle = np.radians(55.)
num_letters = len(text)
radius = 0.925 * CIRCLE_RADIUS
for i, letter in enumerate(text):
    angle = -max_angle + 2. * max_angle * (i / (num_letters - 1)) - 0.5 * np.pi
    x, y = radius * np.cos(angle), radius * np.sin(angle)
    plt.text(x, y, letter, size=20., rotation=np.degrees(angle) + 90., ha='center',
        va='center', color=COLOR_2)

figure(-0.54, 0.54, -0.36, 0.72)
plot_baldaquin(line_color='gray', lw=7., wave=False)

figure(-0.54, 0.54, -0.36, 0.72, background_color='black')
plot_baldaquin(line_color='white', lw=7., wave=False)


plt.show()
