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

from loguru import logger

from baldaquin.config import SampleConfiguration
from baldaquin.gui import stylesheet_file_path, _icon_file_path, QtGui, QtCore, QtWidgets
import baldaquin.widgets


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
    # Run control widget and control bar on the left...
    ctrl_bar = baldaquin.widgets.ControlBar()
    rc_widget = baldaquin.widgets.RunControlCard('NoOp', 'NoOp')
    layout.addWidget(rc_widget, 0, 0)
    layout.addWidget(ctrl_bar, 1, 0)
    # ...and a few tabs on the right.
    tab = QtWidgets.QTabWidget()
    tab.setIconSize(QtCore.QSize(25, 25))
    layout.addWidget(tab, 0, 1, 2, 1)
    config_widget = baldaquin.widgets.ConfigurationWidget(SampleConfiguration())
    tab.addTab(config_widget, '')
    tab.setTabIcon(0, QtGui.QIcon(_icon_file_path('hub')))
    logger_widget = baldaquin.widgets.LoggerDisplay()
    tab.addTab(logger_widget, '')
    tab.setTabIcon(1, QtGui.QIcon(_icon_file_path('chat')))
    # Interact with the widgets a little bit...
    logger.info('Howdy, partner?')
    rc_widget.set_value('uptime', 0.)
    rc_widget.set_value('run_id', 313)
    rc_widget.set_value('station_id', 1)

    return app, window



if __name__ == '__main__':
    app, window = test_gui_elements()
    window.show()
    sys.exit(app.exec_())
