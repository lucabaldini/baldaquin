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

Here is a (non-exhaustive) list of things that we need to keep track of, here.

The .exec() method is used in Qt to start the event loop of your QApplication or
dialog boxes. In Python 2 exec was a keyword, meaning it could not be used for
variable, function or method names. The solution used in both PyQt4 and PySide
was to rename uses of .exec to .exec_() to avoid this conflict. Python 3 removed
the exec keyword, freeing the name up to be used. As a result from PyQt6 .exec()
calls are named just as in Qt. At the time of writing, PySide6 still supports
the exec_() form of things, but PySide6 version 6.4.3 emits a deprecation warning
along the lines of "'exec_' will be removed in the future. Use 'exec' instead."

There is a rather oscure bug in matplotlib triggered by specific combinations of
matplotlib and PySide6, see
https://github.com/matplotlib/matplotlib/issues/24315

"""

import operator
import sys

from loguru import logger

from baldaquin import BALDAQUIN_QT_WRAPPER


def _exec_qapp_old_style(qapp):
    """Old-style QApplication bootstrap call (with the final underscore).
    """
    sys.exit(qapp.exec_())


def _exec_qapp_new_style(qapp):
    """New-style QApplication bootstrap call (without the final underscore).
    """
    sys.exit(qapp.exec())


if BALDAQUIN_QT_WRAPPER == 'PySide6':
    from PySide6 import QtCore, QtGui, QtWidgets
    exec_qapp = _exec_qapp_new_style
    # Horrible workaround for https://github.com/matplotlib/matplotlib/issues/24315
    from matplotlib import __version__, parse_version
    _plt_version = parse_version(__version__)
    if (_plt_version.major, _plt_version.minor, _plt_version.micro) < (3, 6, 2):
        bug_url = 'https://github.com/matplotlib/matplotlib/issues/24315'
        logger.info(f'Monkeypatching matplotlib Qt compatibility layer for {bug_url}...')
        import matplotlib.backends.qt_compat as _qtcompat
        _QT_API = _qtcompat.QT_API
        _qtcompat._to_int = operator.attrgetter('value') if _QT_API in ('PyQt6', 'PySide6') else int


if BALDAQUIN_QT_WRAPPER == 'PySide2':
    from PySide2 import QtCore, QtGui, QtWidgets
    exec_qapp = _exec_qapp_old_style


if BALDAQUIN_QT_WRAPPER == 'PyQt6':
    from PyQt6 import QtCore, QtGui, QtWidgets
    exec_qapp = _exec_qapp_new_style


if BALDAQUIN_QT_WRAPPER == 'PyQt5':
    from PyQt5 import QtCore, QtGui, QtWidgets
    exec_qapp = _exec_qapp_old_style
