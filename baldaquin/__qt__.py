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

"""Convenience module handling the Qt-related import.

This is mainly to handle the possibility of switching from/to PyQy/PySide
in the various available flavors. At the time the baldaquin project was started
there were basically four, slightly different sensible possibilities floating
around (PySide2/6 and PyQt5/6), each with subtle differences in semantics, PySide6
probably being the preferred choice.
"""

from PySide6 import QtCore, QtGui, QtWidgets
