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


"""Custom widgets for the user interface.
"""



import os
import sys
from typing import Any

import loguru
from loguru import logger
from PySide2 import QtCore, QtGui, QtWidgets

from baldaquin import BALDAQUIN_ICONS, BALDAQUIN_SKINS
from baldaquin.config import ConfigurationParameter
import baldaquin.gui



class CardWidget(QtWidgets.QFrame):

    """Small class implementing a (read-only) card.

    According to the material design guidelines
    https://material.io/components/cards
    cards are surfaces that display content and actions on a single topic.
    For our purposes, cards are basically QFrame objects holding a vertical layout
    to which we attach :class:`DisplayWidget <baldaquin.gui.DisplayWidget>`
    instances.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self._widget_dict = {}

    def add_bottom_stretch(self) -> None:
        """Add a vertical stretch at the bottom of the layout.

        This is to ensure that the card item are "floating" in the card container
        without being expanded, and the net effect is that the items appear
        aligned to the top in the card. There might be a clever way to achieve
        this automatically in the loop filling the card, but I could not make it
        work, of not manually.
        """
        self.layout().addStretch()

    def add(self, *args, **kwargs) -> None:
        """Add an item to the card.

        Note the signature, here, is designed to match exactly that of the
        :class:`DisplayWidget <baldaquin.gui.DisplayWidget>` constructor.
        """
        widget = baldaquin.gui.DisplayWidget(*args, **kwargs)
        if widget.name in self._widget_dict:
            raise RuntimeError(f'Duplicated card item name "{widget.name}"')
        self._widget_dict[widget.name] = widget
        self.layout().addWidget(widget)

    def set_value(self, name : str, value : Any):
        """Set the value for a specific card item (addressed by name).

        This will raise a KeyError if the card item does not exist.
        """
        self._widget_dict[name].set_value(value)

    def sizeHint(self) -> QtCore.QSize:
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(200, 400)




class ConfigurationWidget(QtWidgets.QWidget):

    """Basic widget to display and edit an instance of a
    :class:`baldaquin.config.ConfigurationBase` subclass.
    """

    def __init__(self, configuration) -> None:
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.configuration = configuration
        self._widget_dict = {}
        for param in configuration.values():
            widget = self.__param_widget(param)
            self._widget_dict[widget.name] = widget
            self.layout().addWidget(widget)
        self.layout().addStretch()

    @staticmethod
    def __param_widget(param : ConfigurationParameter) -> baldaquin.gui.DataWidgetBase:
        """Turn a configuration parameter into the corresponding widget.

        The fact that we're using two different widgets for ``str`` input,
        depending on whether ``choices`` is set or not, makes this slightly more
        lengthy to code---we could have probably just used a plain dictionary,
        if that was not the case.
        """
        args = param.name, param.intent, param.value, param.units, param.fmt
        kwargs = param.constraints
        type_ = param.type_name
        if type_ == 'bool':
            return baldaquin.gui.ParameterCheckBox(*args, **kwargs)
        if type_ == 'int':
            return baldaquin.gui.ParameterSpinBox(*args, **kwargs)
        if type_ == 'float':
            return baldaquin.gui.ParameterDoubleSpinBox(*args, **kwargs)
        if type_ == 'str':
            if len(kwargs):
                return baldaquin.gui.ParameterLineEdit(*args, **kwargs)
            else:
                return baldaquin.gui.ParameterComboBox(*args, **kwargs)
        raise RuntimeError(f'Unknown parameter type {type_}')

    def set_value(self, name : str, value : Any) -> None:
        """Set the value for a specific parameter (addressed by name).

        Mind this will raise a KeyError if the widget does not exist.
        """
        self._widget_dict[name].set_value(value)

    def sizeHint(self) -> QtCore.QSize:
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(400, 400)




class LoggerDisplay(QtWidgets.QTextEdit):

    """Simple widget to display records from the application logger.

    This is simply connecting a QTextEdit as a sink of the application-wide
    logger, which is made possible by the aweseome loguru library.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        logger.add(self.display)

    def display(self, message : loguru._handler.Message) -> None:
        """Display a single message.
        """
        record = message.record
        #icon = record["level"].icon
        text = f'[{record["time"]}] {record["message"]}\n'
        self.insertPlainText(text)

    def sizeHint(self) -> QtCore.QSize:
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(800, 400)



class ControlBar(QtWidgets.QFrame):

    """Class describing a control bar, that is, a series of QPushButton objects
    arranged horizontally that can be used to control the Run control
    """

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.teardown_button = baldaquin.gui.Button('file_download')
        self.teardown_button.setToolTip('Teardown the run control')
        self.setup_button = baldaquin.gui.Button('file_upload')
        self.setup_button.setToolTip('Setup the run control')
        self.run_button = baldaquin.gui.Button('play_arrow')
        self.run_button.setToolTip('Start/stop the data acquisition')
        layout.addWidget(self.teardown_button)
        layout.addWidget(self.setup_button)
        layout.addWidget(self.run_button)
        self.setLayout(layout)
        self.__running = None
        self.set_stopped()
        self.run_button.clicked.connect(self.toggle_run_button)

    def toggle_run_button(self) -> None:
        """Toggle between the running and stopped states.
        """
        if self.__running:
            self.set_stopped()
        else:
            self.set_running()

    def reset(self) -> None:
        """Set the bar in the reset state.
        """
        self.teardown_button.setEnabled(False)
        self.setup_button.setEnabled(True)
        self.run_button.setEnabled(False)
        self.run_button = Button('play_arrow')

    def set_running(self):
        """Set the bar in the running state.
        """
        self.teardown_button.setEnabled(False)
        self.setup_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.run_button.set_icon('stop')
        self.__running = True

    def set_stopped(self):
        """Set the bar in the stopped state.
        """
        self.teardown_button.setEnabled(True)
        self.setup_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.run_button.set_icon('play_arrow')
        self.__running = False



class RunControlCard(CardWidget):

    """Specialized card to display the run control information.
    """

    def __init__(self, run_contro_name : str, backend_name : str) -> None:
        """Constructor.
        """
        super().__init__()
        self.add('ctrl', 'Run control', run_contro_name)
        self.add('backend', 'Back-end', backend_name)
        self.add('userapp', 'User application')
        self.add('run_id', 'Run Id')
        self.add('station_id', 'Test stand Id')
        self.add('uptime', 'Uptime', 0., units='s', fmt='.3f')
        self.add_bottom_stretch()
