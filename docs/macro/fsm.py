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

"""Finite-state machine diagram.
"""

from baldaquin import BALDAQUIN_DOCS
from baldaquin.plt_ import plt


def diagram_figure(figure_name):
    """Create a white, empty figure.
    """
    plt.figure(figure_name)
    plt.axis('off')


def diagram_box(x: float, y: float, text: str, **kwargs) -> None:
    """Draw a text box.
    """
    kwargs.setdefault('color', 'black')
    kwargs.setdefault('ha', 'center')
    bbox = dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1')
    plt.text(x, y, text, bbox=bbox, **kwargs)


def text(x: float, y: float, text: str, **kwargs):
    """
    """
    kwargs.setdefault('ha', 'center')
    kwargs.setdefault('backgroundcolor', 'white')
    plt.text(x, y, text, **kwargs)


def arrow(start, end, connectionstyle: str = 'arc3,rad=-0.2'):
    """
    """
    _arrowprops = dict(arrowstyle="->", color="0.5", shrinkA=5, shrinkB=5,
                       patchA=None, patchB=None, connectionstyle=connectionstyle)
    plt.annotate('', xy=end, xytext=start, arrowprops=_arrowprops)


def fsm() -> None:
    """Draw the finite-state machine diagram
    """
    diagram_figure('baldaquin_fsm')
    diagram_box(0.0, 0.75, 'RESET')
    arrow((0.075, 0.8), (0.35, 0.8))
    text(0.225, 0.85, 'setup()', va='bottom')
    arrow((0.35, 0.7), (0.075, 0.7))
    text(0.225, 0.65, 'teardown()', va='top')
    diagram_box(0.45, 0.75, 'STOPPED')
    arrow((0.55, 0.8), (0.8, 0.8))
    text(0.675, 0.85, 'start_run()', va='bottom')
    arrow((0.8, 0.7), (0.55, 0.7))
    text(0.675, 0.65, 'stop_run()', va='top')
    diagram_box(0.9, 0.75, 'RUNNING')
    diagram_box(0.675, 0.25, 'PAUSED')
    arrow((0.95, 0.7), (0.775, 0.25))
    text(0.875, 0.4, 'pause()')
    arrow((0.725, 0.325), (0.9, 0.7))
    text(0.775, 0.5, 'resume()')
    arrow((0.575, 0.25), (0.45, 0.7))
    text(0.475, 0.45, 'stop()')


if __name__ == '__main__':
    fsm()
    file_path = BALDAQUIN_DOCS / 'figures' / 'baldaquin_fsm.png'
    plt.savefig(file_path)
    plt.show()
