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
from pathlib import Path
import sys
from typing import Any

import loguru
from loguru import logger
from matplotlib.figure import Figure

from baldaquin.__qt__ import QtCore, QtGui, QtWidgets, exec_qapp
from baldaquin import BALDAQUIN_ICONS, BALDAQUIN_SKINS
from baldaquin.app import UserApplicationBase
from baldaquin.config import ConfigurationParameter, ConfigurationBase, EmptyConfiguration
from baldaquin.hist import HistogramBase
from baldaquin.runctrl import FsmState, RunControlBase

# This needs to stay *after* the from baldaquin.__qt__ import, in order for the
# matplotlib monkeypatching to happen in time.
from matplotlib.backends.backend_qtagg import FigureCanvas



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


def stylesheet_file_path(name : str = 'default') -> Path:
    """Return the path to a given stylesheet file.
    """
    file_name = f'{name}.qss'
    return BALDAQUIN_SKINS / file_name



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
    class member and the ``current_value()`` and ``set_value()`` class methods;
    overloading ``setup()`` is optional.

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

    def current_value(self) -> Any:
        """Return the current value hold by the configuration widget.
        """
        raise NotImplementedError

    def set_value(self, value : Any) -> None:
        """Set hook to be reimplemented by derived classes.
        """
        raise NotImplementedError



class ParameterCheckBox(DataWidgetBase):

    """Check box data widget, mapipng ``bool`` input parameters.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QCheckBox

    def current_value(self) -> bool:
        """Overloaded method.
        """
        return self.value_widget.isChecked()

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

    def current_value(self) -> int:
        """Overloaded method.
        """
        return self.value_widget.value()

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setValue(value)



class ParameterDoubleSpinBox(ParameterSpinBox):

    """Double spin box data widget, mapping ``float`` input parameters.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QDoubleSpinBox

    def current_value(self) -> float:
        """Overloaded method.
        """
        return self.value_widget.value()



class ParameterLineEdit(DataWidgetBase):

    """Line edit data widget, mapping ``str`` input parameters when there is
    no ``choice`` constraint applied.
    """

    VALUE_WIDGET_CLASS = QtWidgets.QLineEdit

    def current_value(self) -> str:
        """Overloaded method.
        """
        return self.value_widget.text()

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

    def current_value(self) -> str:
        """Overloaded method.
        """
        return self.value_widget.currentText()

    def set_value(self, value) -> None:
        """Overloaded method.
        """
        self.value_widget.setCurrentIndex(self.value_widget.findText(value))



class ConfigurationWidget(QtWidgets.QWidget):

    """Basic widget to display and edit an instance of a
    :class:`baldaquin.config.ConfigurationBase` subclass.
    """

    def __init__(self, configuration : ConfigurationBase = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        if configuration is not None:
            self.display(configuration)

    def display(self, configuration : ConfigurationBase) -> None:
        """Display a given configuration.
        """
        # Keep a reference to the input configuration class so that we can return
        # the current (possibly modified) configuration as an instance of the
        # proper class.
        self._config_class = configuration.__class__
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
            if 'choices' in kwargs:
                return ParameterComboBox(*args, **kwargs)
            return ParameterLineEdit(*args, **kwargs)
        raise RuntimeError(f'Unknown parameter type {type_}')

    def current_value(self, name : str) -> Any:
        """Retrieve the current value for a given key.
        """
        return self._widget_dict[name].current_value()

    def set_value(self, name : str, value : Any) -> None:
        """Set the value for a specific parameter (addressed by name).

        This will raise a KeyError if the widget does not exist.
        """
        self._widget_dict[name].set_value(value)

    def sizeHint(self) -> QtCore.QSize:
        """Overloaded method defining the default size.
        """
        return QtCore.QSize(400, 400)

    def current_configuration(self) -> ConfigurationBase:
        """Return the current configuration displayed in the widget.
        """
        configuration = self._config_class()
        for key, widget in self._widget_dict.items():
            configuration.update_value(key, widget.current_value())
        return configuration



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

    #pylint: disable=c-extension-no-member
    started = QtCore.Signal()
    stopped = QtCore.Signal()

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
        self.started.emit()

    def set_stopped(self):
        """Set the bar in the stopped state.
        """
        self.teardown_button.setEnabled(True)
        self.setup_button.setEnabled(False)
        self.run_button.setEnabled(True)
        self.run_button.set_icon('play_arrow')
        self.__running = False
        self.stopped.emit()



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
        if value is None:
            value = DataWidgetBase.MISSING_VALUE_LABEL
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
    _VALUE_DICT = {
        RunControlCardField.UPTIME: 0.
        }
    _KWARGS_DICT = {
        RunControlCardField.UPTIME: dict(units='s', fmt='.3f')
        }



class EventHandlerCardField(Enum):

    """
    """

    FILE_PATH = 'Path to the output file'
    BUFFER_CLASS = 'Data buffer type'
    NUM_EVENTS_PROCESSED = 'Number of events processed'
    AVERAGE_EVENT_RATE = 'Average event rate'
    NUM_EVENTS_WRITTEN = 'Number events written to disk'
    NUM_BYTES_WRITTEN = 'Number of bytes written to disk'


class EventHandlerCard(CardWidget):

    """Specialized card widget for the event handler.
    """

    _FIELD_ENUM = EventHandlerCardField
    _VALUE_DICT = {
        EventHandlerCardField.NUM_EVENTS_PROCESSED: 0,
        EventHandlerCardField.AVERAGE_EVENT_RATE: 0.,
        EventHandlerCardField.NUM_EVENTS_WRITTEN: 0,
        EventHandlerCardField.NUM_BYTES_WRITTEN: 0
        }
    _KWARGS_DICT = {
        EventHandlerCardField.AVERAGE_EVENT_RATE: dict(units='Hz', fmt='.3f')
        }



class PlotCanvasWidget(FigureCanvas):

    """Custom widget to display a matplotlib canvas.

    See https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
    for more information about embedding matplotlib in Qt.

    This specific widget is equipped with a QTimer object that can be used
    to manage the updating of the object.

    Arguments
    ---------
    kwrgs : dict
        The keyword arguments to be passed to the subplot() call.
    """

    UPDATE_TIMER_INTERVAL = 750

    update_started = QtCore.Signal()
    update_stopped = QtCore.Signal()

    def __init__(self, **kwargs) -> None:
        """Constructor.
        """
        super().__init__(Figure())
        self.axes = self.figure.subplots(**kwargs)
        self._update_timer = QtCore.QTimer()
        self._update_timer.setInterval(self.UPDATE_TIMER_INTERVAL)

    def start_updating(self) -> None:
        """Start the update timer.
        """
        self._update_timer.start()
        self.update_started.emit()

    def stop_updating(self) -> None:
        """Stop the update timer.
        """
        self._update_timer.stop()
        self.update_stopped.emit()

    def connect_slot(self, slot) -> None:
        """Connect a slot to the underlying timer managing the canvas update.

        Note that we connect the slot to the update_stopped signal from the
        widget, so that we trigger one last update when the data acquisition is
        stopped.
        """
        self._update_timer.timeout.connect(slot)
        self.update_stopped.connect(slot)

    def clear(self) -> None:
        """Clear the canvas.
        """
        self.axes.clear()

    def draw_histogram(self, histogram : HistogramBase, stat_box : bool = True,
        clear : bool = True, **kwargs):
        """Draw a histogram on the canvas.

        Arguments
        ---------
        histogram : HistogramBase
            The histogram object to be plotted.

        clear : bool
            If True, clear the canvas before the object is plotted.

        kwargs : dict
            The keyword arguments to be passed to the histogram.plot() call.
        """
        if clear:
            self.clear()
        histogram.plot(self.axes, **kwargs)
        if stat_box:
            histogram.stat_box(self.axes)
        self.axes.figure.canvas.draw()



class MainWindow(QtWidgets.QMainWindow):

    """Base class for a DAQ main window.
    """

    PROJECT_NAME = None
    MINIMUM_WIDTH = 1000
    TAB_ICON_SIZE = QtCore.QSize(25, 25)

    #pylint: disable=c-extension-no-member
    start_run = QtCore.Signal(ConfigurationBase)
    stop_run = QtCore.Signal()

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
        self.event_handler_card = EventHandlerCard()
        self.add_tab(self.event_handler_card, 'Event handler', 'share')
        self.user_application_widget = ConfigurationWidget()
        self.add_tab(self.user_application_widget, 'User application', 'sensors')
        # Setup the internal GUI connections.
        self.control_bar.started.connect(self.start_run_control)
        self.control_bar.stopped.connect(self.stop_run_control)

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

    def add_tab(self, page : QtWidgets.QWidget, label : str, icon_name : str = None) -> QtWidgets.QWidget:
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
        return page

    def add_plot_canvas_tab(self, label : str, icon_name : str = None, **kwargs):
        """Add a page to the tab widget holding a matplotlib plot.

        Note that the start_run and stop_run signals of the parent main window are
        automatically connected to the start_updating and stop_updating slots
        of the PlotCanvasWidget object that is added to the tab.

        Arguments
        ---------
        label : str
            The text label to be displayed on the tab.

        icon_name : str, optional
            The name of the icon to be displayed on the tab (if None, non icon is shown).

        kwargs : dict
            All the keyword arguments to be passed to the matplotlib subplots() call.
        """
        widget = PlotCanvasWidget(**kwargs)
        self.start_run.connect(widget.start_updating)
        self.stop_run.connect(widget.stop_updating)
        return self.add_tab(widget, label)

    def add_logger_tab(self) -> LoggerDisplay:
        """Add the default logger tab.
        """
        return self.add_tab(LoggerDisplay(), 'Logger', 'chat')

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

    def set_output_file(self, file_path):
        """
        """
        self.event_handler_card.set(EventHandlerCardField.FILE_PATH, file_path)

    def set_event_handler_stats(self, num_events_processed : int, num_events_written : int,
        num_bytes_written : int, average_event_rate : float) -> None:
        """
        """
        self.event_handler_card.set(EventHandlerCardField.NUM_EVENTS_PROCESSED, num_events_processed)
        self.event_handler_card.set(EventHandlerCardField.NUM_EVENTS_WRITTEN, num_events_written)
        self.event_handler_card.set(EventHandlerCardField.NUM_BYTES_WRITTEN, num_bytes_written)
        self.event_handler_card.set(EventHandlerCardField.AVERAGE_EVENT_RATE, average_event_rate)

    def setup_user_application_widgets(self, user_application) -> None:
        """Set the user application name in the run control card.
        """
        self.run_control_card.set(RunControlCardField.USER_APPLICATION, user_application.NAME)
        self.user_application_widget.display(user_application.configuration)
        user_application.event_handler.output_file_set.connect(self.set_output_file)
        # We might want to connect the buffer_flushed signal, as well.
        buffer_class = user_application.event_handler.BUFFER_CLASS.__name__
        self.event_handler_card.set(EventHandlerCardField.BUFFER_CLASS, buffer_class)

    def set_uptime(self, value : float) -> None:
        """Set the uptime in the run contro card.
        """
        self.run_control_card.set(RunControlCardField.UPTIME, value)

    def start_run_control(self) -> None:
        """Start the run control.

        This is called when the start button on the control bar is pressed.
        """
        user_app_configuration = self.user_application_widget.current_configuration()
        self.start_run.emit(user_app_configuration)

    def stop_run_control(self) -> None:
        """Stop the run control.

        This is called when the stop button on the control bar is pressed.
        """
        self.stop_run.emit()

    def connect_to_run_control(self, run_control : RunControlBase) -> None:
        """Connect the window to a given run control.
        """
        self.set_test_stand_id(run_control._test_stand_id)
        self.set_run_id(run_control._run_id)
        self.set_state(run_control.state())
        run_control.user_application_loaded.connect(self.setup_user_application_widgets)
        run_control.state_changed.connect(self.set_state)
        run_control.run_id_changed.connect(self.set_run_id)
        run_control.uptime_updated.connect(self.set_uptime)
        run_control.event_handler_stats_updated.connect(self.set_event_handler_stats)
        self.start_run.connect(run_control.set_running)
        self.stop_run.connect(run_control.set_stopped)



def bootstrap_qapplication():
    """Create a QApplication object and apply the proper stypesheet.
    """
    #pylint: disable=unspecified-encoding
    qapp = QtWidgets.QApplication(sys.argv)
    with open(stylesheet_file_path(), 'r') as stylesheet:
        qapp.setStyleSheet(stylesheet.read())
    return qapp


def bootstrap_window(window_class, run_control : RunControlBase = None,
    user_application : UserApplicationBase = None) -> None:
    """Bootstrap a main window.

    This is creating a QApplication, applying the relevant stylesheet, and
    creating an actual instance of the window class passed as an argument.
    """
    qapp = bootstrap_qapplication()
    window = window_class()
    if run_control is not None:
        window.connect_to_run_control(run_control)
        if user_application is not None:
            run_control.load_user_application(user_application)
    window.show()
    exec_qapp(qapp)
