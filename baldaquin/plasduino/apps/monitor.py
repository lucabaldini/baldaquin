# Copyright (C) 2024 the baldaquin team.
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

"""Plasduino monitor application.
"""

from baldaquin import logger
from baldaquin import plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.app import UserApplicationBase
from baldaquin.config import ConfigurationBase
from baldaquin.gui import bootstrap_window, MainWindow
from baldaquin.plasduino import PLASDUINO_APP_CONFIG
from baldaquin.plasduino.plasduino import PlasduinoRunControl, PlasduinoAnalogEventHandler
from baldaquin.plasduino.protocol import AnalogReadout
from baldaquin.strip import StripChart



class AppMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME

    def __init__(self, parent : QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.strip_chart_tab = self.add_plot_canvas_tab('Strip charts')

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        plot_strip_charts = lambda :\
            self.strip_chart_tab.draw_strip_charts(*user_application.strip_charts)
        self.strip_chart_tab.connect_slot(plot_strip_charts)



class AppConfiguration(ConfigurationBase):

    """User application configuration.
    """

    PARAMETER_SPECS = (
        ('sampling_interval', 'int', 500, 'Sampling interval', 'ms', 'd', dict(min=100, max=100000)),
        ('ch0', 'int', 0, 'Pin number for channel 0', None, None, dict(min=-1, max=5)),
        ('ch1', 'int', 1, 'Pin number for channel 1', None, None, dict(min=-1, max=5)),
        ('ch2', 'int', -1, 'Pin number for channel 2', None, None, dict(min=-1, max=5)),
        ('ch3', 'int', -1, 'Pin number for channel 3', None, None, dict(min=-1, max=5)),
        ('ch4', 'int', -1, 'Pin number for channel 4', None, None, dict(min=-1, max=5)),
        ('ch5', 'int', -1, 'Pin number for channel 5', None, None, dict(min=-1, max=5))
    )

    def sketch_parameters(self):
        """Return the parameters that are necessary for the configuration of the
        sketch on the arduino side.
        """
        pin_list = []
        for i in range(6):
            pin = self.value(f'ch{i}')
            if pin in pin_list:
                raise RuntimeError(f'Duplicated pin in {self.__class__.__name__}')
            if pin >= 0:
                pin_list.append(pin)
        sampling_interval = self.value('sampling_interval')
        return pin_list, sampling_interval



class GenericMonitor(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Generic monitor'
    CONFIGURATION_CLASS = AppConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'monitor.cfg'
    EVENT_HANDLER_CLASS = PlasduinoAnalogEventHandler

    def configure(self):
        """Overloaded method.
        """
        pin_list, sampling_interval = self.configuration.sketch_parameters()
        kwargs = dict(xlabel='Time [s]', ylabel='ADC counts')
        self.strip_charts = [StripChart(100, f'Pin {pin}', **kwargs) for pin in pin_list]
        self.event_handler.serial_interface.setup_analog_sampling_sketch(pin_list,
            sampling_interval)

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()

    def teardown(self) -> None:
        """Overloaded method (STOPPED -> RESET).
        """
        self.event_handler.close_serial_interface()

    def start_run(self) -> None:
        """Overloaded method.
        """
        self.event_handler.serial_interface.write_start_run()
        super().start_run()

    def stop_run(self) -> None:
        """Overloaded method.
        """
        self.event_handler.serial_interface.write_stop_run()
        super().stop_run()
        num_bytes = self.event_handler.serial_interface.in_waiting
        logger.info(f'{num_bytes} bytes remaining in the input serial buffer...')
        data = self.event_handler.serial_interface.read(num_bytes)
        logger.info('Flushing the serial port...')
        self.event_handler.serial_interface.flush()

    def process_packet(self, packet) -> None:
        """Overloaded method.
        """
        readout = AnalogReadout.unpack(packet)
        self.strip_charts[readout.pin_number].append(readout.timestamp, readout.adc_value)



if __name__ == '__main__':
    bootstrap_window(AppMainWindow, PlasduinoRunControl(), GenericMonitor())
