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

from loguru import logger
from PySide2 import QtCore, QtGui, QtWidgets

from baldaquin import BALDAQUIN_ICONS, BALDAQUIN_SKINS


_DEFAULT_ICON_CATALOG = 'material3'
_DEFAULT_ICON_STYLE = 'FILL0_wght400_GRAD0_opsz48'


def _icon_file_path(name : str, catalog : str = _DEFAULT_ICON_CATALOG, fmt : str = 'svg',
    style : str = _DEFAULT_ICON_STYLE):
    """Return the path to a given icon file.
    """
    file_name = f'{name}_{style}.{fmt}'
    file_path = os.path.join(BALDAQUIN_ICONS, catalog, file_name)
    return file_path


def _stylesheet_file_path(name : str = 'default'):
    """Return the path to a given stylesheet file.
    """
    file_name = f'{name}.qss'
    file_path = os.path.join(BALDAQUIN_SKINS, file_name)
    return file_path



class Button(QtWidgets.QPushButton):

    """Default round button.
    """

    def __init__(self, icon_name, size : int = 40, icon_size : int = 25):
        """Constructor.
        """
        super().__init__()
        self.setFixedSize(size, size)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.set_icon(icon_name)

    def set_icon(self, icon_name : str, icon_size : int = 25):
        """
        """
        self.setIcon(QtGui.QIcon(_icon_file_path(icon_name)))
        self.setIconSize(QtCore.QSize(icon_size, icon_size))



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




class CardItem(QtWidgets.QWidget):

    """Small class containing a (read-only) card item.

    In our implementation, a card item is the datum of two QLabel objects
    containing text: a title and a value. They are arranged into a vertical
    layout, one on top of the other.

    Note that the title and value QLabel objects have specific objects names
    attached to them to make it possible to style them via stylesheets
    downstream.

    Arguments
    ---------
    name : str
        The name of the card---mind this is the key for addressing items within
        a Card object.

    title : str
        The title of the item.

    value
        The value hold by the card item.

    units : str
        The units attach to the card item value.

    fmt : str
        The format string to be used to render the card item value.
    """

    TITLE_OBJECT_NAME = 'card_item_title'
    VALUE_OBJECT_NAME = 'card_item_value'
    MISSING_VALUE = '-'

    def __init__(self, name : str, title : str, value=None, units : str = None,
        fmt : str = None) -> None:
        """Constructor
        """
        self.name = name
        self._units = units
        self._fmt = fmt
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName(self.TITLE_OBJECT_NAME)
        self.value_label = QtWidgets.QLabel()
        self.value_label.setObjectName(self.VALUE_OBJECT_NAME)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.set_title(title)
        if value is not None:
            self.set_value(value)
        else:
            self.set_value(self.MISSING_VALUE)

    def set_title(self, title : str) -> None:
        """Set the title for the card item.
        """
        self.title_label.setText(title)

    def set_value(self, value) -> None:
        """Set the value for the card item.
        """
        text = f'{value:{self._fmt if self._fmt else ""}} {self._units if self._units else ""}'
        self.value_label.setText(text)



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

    tab_card = Card()
    tab_card.add_item('ip', 'IP address', '127.0.0.1')
    tab_card.add_item('port', 'Port', '12')
    tab_card.layout().addStretch()
    tab.addTab(tab_card, '')
    tab.setTabIcon(1, QtGui.QIcon(_icon_file_path('hub')))


    rc_card.set_user_application('my_application.py')
    rc_card.set_uptime(12.34)

    logger.info('Hi...')
    logger.info('...there!')

    window.show()
    sys.exit(app.exec_())
