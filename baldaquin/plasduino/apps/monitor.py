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

"""Plasduino monitor application.
"""

import time

import numpy as np

from baldaquin import logger
from baldaquin.__qt__ import QtWidgets
from baldaquin.app import UserApplicationBase
from baldaquin.buf import CircularBuffer
from baldaquin.config import ConfigurationBase
from baldaquin.event import EventHandlerBase
from baldaquin.gui import bootstrap_window, MainWindow
from baldaquin.plasduino import PLASDUINO_APP_CONFIG, PLASDUINO_PROJECT_NAME
from baldaquin.plasduino.protocol import PlasduinoSerialInterface, AnalogReadout
from baldaquin.runctrl import RunControlBase
from baldaquin.plasduino.__serial__ import arduino_info



class AppMainWindow(MainWindow):

    """
    """

    PROJECT_NAME = PLASDUINO_PROJECT_NAME



class AppConfiguration(ConfigurationBase):

    """User application configuration.
    """

    TITLE = 'Monitor configuration'
    PARAMETER_SPECS = (
        ('sampling_interval', 'int', 500, 'Sampling interval', 'ms', 'd', dict(min=100, max=100000)),
    )


class AppRunControl(RunControlBase):

    """Mock run control for testing purposes.
    """

    PROJECT_NAME = PLASDUINO_PROJECT_NAME



class AppEventHandler(EventHandlerBase):

    """Mock event handler for testing purpose.
    """

    BUFFER_CLASS = CircularBuffer
    BUFFER_KWARGS = dict(max_size=20, flush_size=10, flush_interval=2.)

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self.serial_interface = None

    def open_serial_interface(self):
        """
        """
        port, model, vid, pid = arduino_info()
        self.serial_interface = PlasduinoSerialInterface(port)
        self.serial_interface.pulse_dtr()
        logger.info('Hand-shaking with the arduino board...')
        sketch_id = self.serial_interface.read_uint8()
        sketch_version = self.serial_interface.read_uint8()
        logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')

    def read_event_data(self):
        """Read a single event.
        """
        return self.serial_interface.read(AnalogReadout.LENGTH)



class Application(UserApplicationBase):

    """Simplest possible user application for testing purposes.
    """

    NAME = 'Temperature monitor'
    CONFIGURATION_CLASS = AppConfiguration
    CONFIGURATION_FILE_PATH = PLASDUINO_APP_CONFIG / 'monitor.cfg'
    EVENT_HANDLER_CLASS = AppEventHandler

    def __init__(self):
        """Overloaded constructor.
        """
        super().__init__()

    def setup(self):
        """
        """
        self.event_handler.open_serial_interface()

    def configure(self):
        """Overloaded method.
        """
        print(self.configuration)
        logger.info(f'Nothing to do in Application.configure()')

    def start_run(self):
        """
        """
        self.event_handler.serial_interface.setup_analog_sampling_sketch((0, 1), 500)
        self.event_handler.serial_interface.write_start_run()
        super().start_run()

    def stop_run(self):
        """
        """
        self.event_handler.serial_interface.write_stop_run()
        super().stop_run()
        num_bytes = self.event_handler.serial_interface.in_waiting
        logger.info(f'{num_bytes} bytes remaining in the input serial buffer...')
        data = self.event_handler.serial_interface.read(num_bytes)
        logger.info('Flushing the serial port...')
        self.event_handler.serial_interface.flush()

    def process_event_data(self, event_data):
        """Dumb data processing routine---print out the actual event.
        """
        readout = AnalogReadout.unpack(event_data)
        print(readout)



if __name__ == '__main__':
    bootstrap_window(AppMainWindow, AppRunControl(), Application())
