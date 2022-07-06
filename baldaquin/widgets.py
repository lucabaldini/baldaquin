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

from loguru import logger
from PySide2 import QtCore, QtGui, QtWidgets

from baldaquin import BALDAQUIN_ICONS, BALDAQUIN_SKINS
from baldaquin.gui import CheckBoxDataWidget, SpinBoxDataWidget, DoubleSpinBoxDataWidget,\
    LineEditDataWidget, DataWidgetBase


class CardWidget(QtWidgets.QFrame):

    """Simple card widget to display information in read-only mode.
    """




class ConfigurationWidget(QtWidgets.QFrame):

    """Basic widget to display and edit an instance of a
    :class:`baldaquin.config.ConfigurationBase` subclass.
    """

    __WIDGET_DICT = {
        'bool': CheckBoxDataWidget,
        'int' : SpinBoxDataWidget,
        'float': DoubleSpinBoxDataWidget,
        'str': LineEditDataWidget
    }

    def __init__(self, configuration):
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.configuration = configuration
        self._item_dict = {}
        for param in configuration.values():
            cls = self.__WIDGET_DICT[param.type_name]
            text = f'{param.intent}'
            item = DataWidgetBase(cls, param.name, text, param.value)
            self._item_dict[item.name] = item
            self.layout().addWidget(item)
        self.layout().addStretch()

    def set_value(self, name, value):
        """Set the value for a specific card item (addressed by name).

        This will raise a KeyError if the card item does not exist.
        """
        self._item_dict[name].set_value(value)



class ControlBar(QtWidgets.QFrame):

    """
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        layout = QtWidgets.QHBoxLayout()
        self.teardown_button = Button('file_download')
        self.teardown_button.setToolTip('Teardown the run control')
        self.setup_button = Button('file_upload')
        self.setup_button.setToolTip('Setup the run control')
        self.run_button = Button('play_arrow')
        self.run_button.setToolTip('Start/stop the data acquisition')
        layout.addWidget(self.teardown_button)
        layout.addWidget(self.setup_button)
        layout.addWidget(self.run_button)
        self.setLayout(layout)
        self.__running = None
        self.set_stopped()
        self.run_button.clicked.connect(self.toggle_run_button)

    def reset(self):
        """
        """
        self.teardown_button.setEnabled(False)
        self.setup_button.setEnabled(True)
        self.run_button.setEnabled(False)
        self.run_button = Button('play_arrow')

    def set_running(self):
        """
        """
        self.teardown_button.setEnabled(False)
        self.setup_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.run_button.set_icon('stop')
        self.__running = True

    def set_stopped(self):
        """
        """
        self.teardown_button.setEnabled(True)
        self.setup_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.run_button.set_icon('play_arrow')
        self.__running = False

    def toggle_run_button(self):
        """
        """
        if self.__running:
            self.set_stopped()
        else:
            self.set_running()








class CardItem(DataWidgetBase):

    """
    """

    def __init__(self, name : str, title : str, value=None, units : str = None,
        fmt : str = None) -> None:
        """Constructor
        """
        super().__init__(QtWidgets.QLabel, name, title, value, units, fmt)

    def set_value(self, value) -> None:
        """Set the value for the card item.
        """
        text = f'{value:{self._fmt if self._fmt else ""}} {self._units if self._units else ""}'
        self.value_widget.setText(text)


class Card(QtWidgets.QFrame):

    """Small class implementing a (read-only) card.

    According to the material design guidelines
    https://material.io/components/cards
    cards are surfaces that display content and actions on a single topic.

    For our purposes, cards are basically QFrame object holding a vertical layout
    to which we attach CardItem objects.
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self._item_dict = {}

    def add_bottom_stretch(self):
        """Add a vertical stretch at the bottom of the layout.

        This is to ensure that the card item are "floating" in the card container
        without being expanded, and the net effect is that the items appear
        aligned to the top in the card. There might be a clever way to achieve
        this automatically in the loop filling the card, but I could not make it
        work, of not manually.
        """
        self.layout().addStretch()

    def add_item(self, *args, **kwargs) -> None:
        """Add an item to the card.

        Note the signature, here, is designed to match exactly that of the
        CardItem constructor.
        """
        item = CardItem(*args, **kwargs)
        if item.name in self._item_dict:
            raise RuntimeError(f'Duplicated card item name "{item.name}"')
        self._item_dict[item.name] = item
        self.layout().addWidget(item)

    def set_value(self, name, value):
        """Set the value for a specific card item (addressed by name).

        This will raise a KeyError if the card item does not exist.
        """
        self._item_dict[name].set_value(value)



class RunControlCard(Card):

    """Specialized card to display the run control information.
    """

    def __init__(self, run_contro_name : str, backend_name : str):
        """Constructor.
        """
        super().__init__()
        self.add_item('ctrl', 'Run control', run_contro_name)
        self.add_item('backend', 'Back-end', backend_name)
        self.add_item('userapp', 'User application')
        self.add_item('uptime', 'Uptime', 0., units='s', fmt='.3f')
        self.add_bottom_stretch()

    def set_user_application(self, value : str):
        """Set the user application.
        """
        self.set_value('userapp', value)

    def set_uptime(self, value : float):
        """Set the uptime.
        """
        self.set_value('uptime', value)



class LoggerDisplay(QtWidgets.QTextEdit):

    """Simple widget to display records from the application logger.
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        logger.add(self.display)

    def display(self, message):
        """
        """
        record = message.record
        #icon = record["level"].icon
        text = f'[{record["time"]}] {record["message"]}\n'
        self.insertPlainText(text)

    def sizeHint(self):
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(800, 400)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    with open(_stylesheet_file_path(), 'r') as f:
        app.setStyleSheet(f.read())
    window = QtWidgets.QMainWindow()
    widget = QtWidgets.QWidget()
    window.setCentralWidget(widget)
    layout = QtWidgets.QGridLayout()
    widget.setLayout(layout)
    bar = ControlBar()
    rc_card = RunControlCard('NoOp', 'NoOp')
    layout.addWidget(rc_card, 0, 0)
    layout.addWidget(bar, 1, 0)

    tab = QtWidgets.QTabWidget()
    tab.setIconSize(QtCore.QSize(25, 25))
    layout.addWidget(tab, 0, 1, 2, 1)

    log_display = LoggerDisplay()
    tab.addTab(log_display, '')
    tab.setTabIcon(0, QtGui.QIcon(_icon_file_path('chat')))

    #tab_card = Card()
    #tab_card.add_item('ip', 'IP address', '127.0.0.1')
    #tab_card.add_item('port', 'Port', '12')
    #tab_card.layout().addStretch()
    #tab.addTab(tab_card, '')
    #tab.setTabIcon(1, QtGui.QIcon(_icon_file_path('hub')))

    from baldaquin.config import SampleConfiguration
    config = SampleConfiguration()
    tab_config = ConfigurationInput(config)
    tab.addTab(tab_config, '')
    tab.setTabIcon(1, QtGui.QIcon(_icon_file_path('hub')))

    rc_card.set_user_application('my_application.py')
    rc_card.set_uptime(12.34)

    logger.info('Hi...')
    logger.info('...there!')

    window.show()
    sys.exit(app.exec_())
