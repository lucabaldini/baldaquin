# Copyright (C) 2022--2023 the baldaquin team.
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


"""Basic GUI elements.
"""

from pathlib import Path
import sys

from baldaquin import BALDAQUIN_SKINS
from baldaquin._qt import QtCore, QtGui, QtWidgets
from baldaquin.runctrl import FsmState, RunControlBase
from baldaquin.widgets import ControlBar, RunControlCard, LoggerDisplay, load_icon,\
    RunControlCardField


def stylesheet_file_path(name : str = 'default') -> Path:
    """Return the path to a given stylesheet file.
    """
    file_name = f'{name}.qss'
    return BALDAQUIN_SKINS / file_name



class MainWindow(QtWidgets.QMainWindow):

    """Base class for a DAQ main window.
    """

    PROJECT_NAME = None
    MINIMUM_WIDTH = 500
    TAB_ICON_SIZE = QtCore.QSize(25, 25)

    def __init__(self, parent : QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__(parent)
        self.setCentralWidget(QtWidgets.QWidget())
        self.centralWidget().setLayout(QtWidgets.QGridLayout())
        self.centralWidget().setMinimumWidth(self.MINIMUM_WIDTH)
        self.control_bar = ControlBar()
        self.add_widget(self.control_bar, 1, 0)
        self.run_control_card = RunControlCard()
        self.run_control_card.set(RunControlCardField.PROJECT_NAME, self.PROJECT_NAME)
        self.add_widget(self.run_control_card, 0, 0)
        self.tab_widget = QtWidgets.QTabWidget()
        #tab.setTabPosition(tab.TabPosition.West)
        self.tab_widget.setIconSize(self.TAB_ICON_SIZE)
        self.add_widget(self.tab_widget, 0, 1, 2, 1)

    def add_widget(self, widget : QtWidgets.QWidget, row : int, col : int,
        row_span : int = 1, col_span : int = 1,
        align : QtCore.Qt.Alignment = QtCore.Qt.Alignment()) -> None:
        """Add a widget to the underlying layout.

        This is just a convenience method mimicking the corresponding hook of the
        underlying layout.

        Arguments
        ---------
        widget : QtWidgets.QWidget
            The widget to be added to the underlying layout.

        row : int
            The starting row position for the widget.

        col : int
            The starting column position for the widget.

        row_span : int, optional (default 1)
            The number of rows spanned by the widget.

        col_span : int, optional (default 1)
            The number of columns spanned by the widget.

        align : QtCore.Qt.Alignment
            The alignment for the widget.
        """
        #pylint: disable=too-many-arguments
        self.centralWidget().layout().addWidget(widget, row, col, row_span, col_span, align)

    def add_tab(self, page : QtWidgets.QWidget, label : str, icon_name : str = None) -> None:
        """Add a page to the tab widget.

        Arguments
        ---------
        page : QtWidgets.QWidget
            The widget to be added to the tab widget.

        label : str
            The text label to be displayed on the tab.

        icon_name : str, optional
            The name of the icon to be displayed on the tab (if None, non icon is shown).
        """
        pos = self.tab_widget.addTab(page, label)
        if icon_name is not None:
            self.tab_widget.setTabIcon(pos, load_icon(icon_name))

    def add_logger_tab(self) -> None:
        """Add the default logger tab.
        """
        self.add_tab(LoggerDisplay(), 'Logger', 'chat')

    def set_test_stand_id(self, test_stand_id : int) -> None:
        """Set the test stand ID in the run control card.
        """
        self.run_control_card.set(RunControlCardField.TEST_STAND_ID, test_stand_id)

    def set_run_id(self, run_id : int) -> None:
        """Set the test run ID in the run control card.
        """
        self.run_control_card.set(RunControlCardField.RUN_ID, run_id)

    def set_state(self, state : FsmState) -> None:
        """Set the test run control state in the run control card.
        """
        self.run_control_card.set(RunControlCardField.STATE, state.value)

    def set_user_application_name(self, name : str) -> None:
        """
        """
        self.run_control_card.set(RunControlCardField.USER_APPLICATION, name)

    def set_uptime(self, value : float):
        """
        """
        self.run_control_card.set(RunControlCardField.UPTIME, value)

    def connect_to_run_control(self, run_control : RunControlBase) -> None:
        """Connect the window to a given run control.
        """
        self.set_test_stand_id(run_control._test_stand_id)
        self.set_run_id(run_control._run_id)
        self.set_state(run_control.state())
        run_control.user_application_loaded.connect(self.set_user_application_name)
        run_control.state_changed.connect(self.set_state)
        run_control.run_id_changed.connect(self.set_run_id)
        run_control.uptime_updated.connect(self.set_uptime)
        self.control_bar.started.connect(run_control.set_running)
        self.control_bar.stopped.connect(run_control.set_stopped)



def bootstrap_window(window_class):
    """Bootstrap a main window.

    This is creating a QApplication, applying the relevant stylesheet, and
    creating an actual instance of the window class passed as an argument.
    """
    #pylint: disable=unspecified-encoding
    app = QtWidgets.QApplication(sys.argv)
    with open(stylesheet_file_path(), 'r') as stylesheet:
        app.setStyleSheet(stylesheet.read())
    window = window_class()
    return app, window
