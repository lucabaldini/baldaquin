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

"""Test suite for gui.py
"""

import sys

from baldaquin.gui import *


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
    # Read-only widgets.
    layout.addWidget(DisplayWidget('w1', 'Something', 313), 0, 0)
    layout.addWidget(DisplayWidget('w2', 'Something else', 12.3, 'm', '.3f'), 1, 0)
    # Read/write widgets
    layout.addWidget(ParameterCheckBox('w3', 'Bool', True), 0, 1)
    layout.addWidget(ParameterSpinBox('w4', 'A spin box', 13, 'ADC counts', min=10, max=20, step=2), 1, 1)
    layout.addWidget(ParameterLineEdit('w5', 'A line edit', 'test'), 2, 1)
    layout.addWidget(ParameterComboBox('w6', 'Pick your choice', 'c3', choices=('c1', 'c2', 'c3')), 3, 1)
    layout.addWidget(ParameterDoubleSpinBox('w7', 'Timeout', 2., 's', min=0., max=10.), 4, 1)
    return app, window



if __name__ == '__main__':
    app, window = test_gui_elements()
    window.show()
    sys.exit(app.exec_())
