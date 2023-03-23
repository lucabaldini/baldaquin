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


"""Custom widgets for the user interface.
"""

from enum import Enum
from typing import Any

import loguru
from loguru import logger

from baldaquin import BALDAQUIN_ICONS
from baldaquin.config import ConfigurationParameter
from baldaquin._qt import QtCore, QtGui, QtWidgets


_DEFAULT_ICON_CATALOG = 'material3'
_DEFAULT_ICON_STYLE = 'FILL0_wght400_GRAD0_opsz48'


def _icon_file_path(name : str, catalog : str = _DEFAULT_ICON_CATALOG, fmt : str = 'svg',
    style : str = _DEFAULT_ICON_STYLE) -> str:
    """Return the path to a given icon file.

    Note this is returning a string, rather than a Path object, as the function
    is mainly used in Qt calls, where Path objects are not readily understood.
    """
    file_name = f'{name}_{style}.{fmt}'
    return f'{BALDAQUIN_ICONS / catalog / file_name}'


def load_icon(name : str, catalog : str = _DEFAULT_ICON_CATALOG, fmt : str = 'svg',
    style : str = _DEFAULT_ICON_STYLE) -> QtGui.QIcon:
    """Load an icon from the given catalog.
    """
    return QtGui.QIcon(_icon_file_path(name, catalog, fmt, style))



class Button(QtWidgets.QPushButton):

    """Small wrapper aroung the QtWidgets.QPushButton class.
    """

    #pylint: disable=too-few-public-methods

    def __init__(self, icon_name : str, size : int = 40, icon_size : int = 25) -> None:
        """Constructor.
        """
        super().__init__()
        self.setFixedSize(size, size)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.set_icon(icon_name, icon_size)

    def set_icon(self, icon_name : str, icon_size : int = 25) -> None:
        """Set the button icon.
        """
        self.setIcon(load_icon(icon_name))
        self.setIconSize(QtCore.QSize(icon_size, icon_size))



class DataWidgetBase(QtWidgets.QWidget):

    """Base class for a widget holding a single piece of information.

    This is nothing more than a pair of widget---a QLabel holding a title and
    a generic widget holding some data---arranged in a vertical layout.
    This is an abstract class, and specialized subclasses are provided below
    to show or edit data in different fashions, representing the basic building
    block to construct complex user interfaces.

    Derived classes must override, at the very minimum, the ``VALUE_WIDGET_CLASS``
    class member and the ``set_value`` class method; overloading ``setup()``
    is instead optional.

    Note that the constructor of this base class calls the ``setObjectName()``
    method for both widgets (with different arguments) to make it easier to
    stylesheet the application downstream.
    """

    VALUE_WIDGET_CLASS = None
    TITLE_WIDGET_NAME = 'data_widget_title'
    VALUE_WIDGET_NAME = 'data_widget_value'
    MISSING_VALUE_LABEL = '-'
    VALUE_WIDGET_HEIGHT = 30

    def __init__(self, name : str, title : str = None, value=None, units : str = None,
                 fmt : str = None, **kwargs) -> None:
        """Constructor
        """
        #pylint: disable=not-callable, too-many-arguments
        if title is None:
            title = name
        self.name = name
        self._units = units
        self._fmt = fmt
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.title_widget = QtWidgets.QLabel()
        self.title_widget.setObjectName(self.TITLE_WIDGET_NAME)
        self.value_widget = self.VALUE_WIDGET_CLASS()
        self.value_widget.setObjectName(self.VALUE_WIDGET_NAME)
        self.value_widget.setFixedHeight(self.VALUE_WIDGET_HEIGHT)
        self.layout().addWidget(self.title_widget)
        self.layout().addWidget(self.value_widget)
        self.set_title(title)
        self.setup(**kwargs)
        if value is not None:
            self.set_value(value)
        else:
            self.set_value(self.MISSING_VALUE_LABEL)

    def setup(self, **kwargs):
        """Do nothing post-construction hook that can be overloaded in derived classes.
        """

    def set_title(self, title : str) -> None:
        """Set the widget title.
        """
        self.title_widget.setText(title)

    def set_value(self, value : Any) -> None:
        """Set hook to be reimplemented by derived classes.
        """
        raise NotImplementedError




class ParameterCheckBox(DataWidgetBase):

    """Check box data widget, mapipng ``bool`` input parameters.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QCheckBox

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setChecked(value)



class ParameterSpinBox(DataWidgetBase):

    """Spin box data widget, mapping ``int`` input parameters.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QSpinBox

    def setup(self, **kwargs) -> None:
        """Overloaded method.
        """
        if self._units is not None:
            self.value_widget.setSuffix(f' {self._units}')
        for key, value in kwargs.items():
            if key == 'min':
                self.value_widget.setMinimum(value)
            elif key == 'max':
                self.value_widget.setMaximum(value)
            elif key == 'step':
                self.value_widget.setSingleStep(value)

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setValue(value)



class ParameterDoubleSpinBox(ParameterSpinBox):

    """Double spin box data widget, mapping ``float`` input parameters.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QDoubleSpinBox



class ParameterLineEdit(DataWidgetBase):

    """Line edit data widget, mapping ``str`` input parameters when there is
    no ``choice`` constraint applied.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QLineEdit

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setText(value)



class ParameterComboBox(DataWidgetBase):

    """Combo box data widget, mapping ``str`` input parameters when there is
    a ``choice`` constraint applied.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QComboBox

    def setup(self, **kwargs) -> None:
        """Overloaded method.
        """
        self.value_widget.addItems(kwargs.get('choices', ()))

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setCurrentIndex(self.value_widget.findText(value))



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
    def __param_widget(param : ConfigurationParameter) -> DataWidgetBase:
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
            return ParameterCheckBox(*args, **kwargs)
        if type_ == 'int':
            return ParameterSpinBox(*args, **kwargs)
        if type_ == 'float':
            return ParameterDoubleSpinBox(*args, **kwargs)
        if type_ == 'str':
            if len(kwargs):
                return ParameterLineEdit(*args, **kwargs)
            return ParameterComboBox(*args, **kwargs)
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



class DisplayWidget(DataWidgetBase):

    """Simple widget to display a single piece of information in a read-only fashion.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QLabel

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        text = f'{value:{self._fmt if self._fmt else ""}} {self._units if self._units else ""}'
        self.value_widget.setText(text)



class CardWidget(QtWidgets.QFrame):

    """Small class implementing a (read-only) card.

    According to the material design guidelines
    https://material.io/components/cards
    cards are surfaces that display content and actions on a single topic.
    For our purposes, cards are basically QFrame objects holding a vertical layout
    to which we attach :class:`DisplayWidget <baldaquin.widget.DisplayWidget>`
    instances.
    """

    _FIELD_ENUM : Enum = ()
    _VALUE_DICT = {}
    _KWARGS_DICT = {}

    def __init__(self, add_bottom_stretch : bool = True) -> None:
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        self._widget_dict = {}
        for field in self._FIELD_ENUM:
            value = self._VALUE_DICT.get(field)
            kwargs = self._KWARGS_DICT.get(field, {})
            self.add(field.value, None, value, **kwargs)
        if add_bottom_stretch:
            self.add_bottom_stretch()

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
        :class:`DisplayWidget <baldaquin.widget.DisplayWidget>` constructor.
        """
        widget = DisplayWidget(*args, **kwargs)
        if widget.name in self._widget_dict:
            raise RuntimeError(f'Duplicated card item name "{widget.name}"')
        self._widget_dict[widget.name] = widget
        self.layout().addWidget(widget)

    def set(self, name : str, value : Any):
        """Set the value for a specific card item (addressed by name).

        This will raise a KeyError if the card item does not exist.
        """
        if isinstance(name, Enum):
            name = name.value
        self._widget_dict[name].set_value(value)

    def sizeHint(self) -> QtCore.QSize:
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(200, 400)



class RunControlCardField(Enum):

    """Definition of the relevant fields for the run control card.

    This is done with the intent of making the process of updating the values of
    the card less error-prone.
    """

    PROJECT_NAME = 'Project'
    USER_APPLICATION = 'User application'
    TEST_STAND_ID = 'Test stand'
    RUN_ID = 'Run ID'
    STATE = 'State'
    UPTIME = 'Uptime'



class RunControlCard(CardWidget):

    """Specialized card to display the run control information.
    """
    _FIELD_ENUM = RunControlCardField
    _VALUE_DICT = {RunControlCardField.UPTIME: 0.}
    _KWARGS_DICT = {RunControlCardField.UPTIME: dict(units='s', fmt='.3f')}
