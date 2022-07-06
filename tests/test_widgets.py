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

import sys

from baldaquin.config import SampleConfiguration
from baldaquin.gui import stylesheet_file_path
from baldaquin.widgets import *


def test_gui_elements():
    """Create a test window to display a the relevant graphical elements.
    """
    app = QtWidgets.QApplication(sys.argv)
    with open(stylesheet_file_path(), 'r') as f:
        app.setStyleSheet(f.read())
    window = QtWidgets.QMainWindow()
    window.setCentralWidget(QtWidgets.QWidget())
    layout = QtWidgets.QGridLayout()
    window.centralWidget().setLayout(layout)
    window.centralWidget().setMinimumWidth(500)

    rc_card = RunControlCard('NoOp', 'NoOp')
    layout.addWidget(rc_card, 0, 0)

    config_widget = ConfigurationWidget(SampleConfiguration())
    layout.addWidget(config_widget, 0, 1)

    return app, window



if __name__ == '__main__':
    app, window = test_gui_elements()
    window.show()
    sys.exit(app.exec_())
