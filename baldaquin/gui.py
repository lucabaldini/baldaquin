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


"""Basic GUI elements.
"""

import os
from typing import Any

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


def stylesheet_file_path(name : str = 'default'):
    """Return the path to a given stylesheet file.
    """
    file_name = f'{name}.qss'
    file_path = os.path.join(BALDAQUIN_SKINS, file_name)
    return file_path


#pylint: disable=c-extension-no-member


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
        self.setIcon(QtGui.QIcon(_icon_file_path(icon_name)))
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

    def __init__(self, name : str, title : str, value=None, units : str = None,
                 fmt : str = None, **kwargs) -> None:
        """Constructor
        """
        #pylint: disable=not-callable, too-many-arguments
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



class DisplayWidget(DataWidgetBase):

    """Simple widget to display a single piece of information in a read-only fashion.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QLabel

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        text = f'{value:{self._fmt if self._fmt else ""}} {self._units if self._units else ""}'
        self.value_widget.setText(text)



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
