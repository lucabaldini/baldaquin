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

"""Test suite for widgets.py
"""

from loguru import logger

from baldaquin.__qt__ import exec_qapp
from baldaquin.gui import MainWindow, RunControlCardField, bootstrap_window


def _test_main_window():
    """Create a test window to display a the relevant graphical elements.
    """
    app, window = bootstrap_window(MainWindow)
    # Interact with the widgets a little bit...
    logger.info('Howdy, partner?')
    window.run_control_card.set(RunControlCardField.UPTIME, 12.)
    window.run_control_card.set(RunControlCardField.TEST_STAND_ID, 1)
    window.run_control_card.set(RunControlCardField.RUN_ID, 313)
    return app, window


if __name__ == '__main__':
    qapp, qwindow = _test_main_window()
    qwindow.show()
    exec_qapp(qapp)
