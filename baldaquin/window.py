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

"""Application windows.
"""

import sys

from baldaquin._qt import QtCore, QtGui, QtWidgets
from baldaquin.gui import stylesheet_file_path


class MainWindow(QtWidgets.QMainWindow):

    """Basic main window class.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    with open(stylesheet_file_path(), 'r') as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
