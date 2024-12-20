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

"""Plasduino top-level module.
"""

from baldaquin import logger
from baldaquin.app import UserApplicationBase
from baldaquin.gui import MainWindow
from baldaquin.event import EventHandlerBase
from baldaquin.plasduino import PLASDUINO_PROJECT_NAME
from baldaquin.plasduino.protocol import PlasduinoSerialInterface
from baldaquin.runctrl import RunControlBase
from baldaquin.__qt__ import QtWidgets
from baldaquin.plasduino.__serial__ import arduino_info


class PlasduinoRunControl(RunControlBase):

    """Mock run control for testing purposes.
    """

    PROJECT_NAME = PLASDUINO_PROJECT_NAME

    def setup(self):
        """
        """
        port, model, vid, pid = arduino_info()
        self.interface = PlasduinoSerialInterface(port)
        self.interface.pulse_dtr()
        logger.info('Hand-shaking with the arduino board...')
        sketch_id = self.interface.read_uint8()
        sketch_version = self.interface.read_uint8()
        logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')

    def start_run(self):
        """
        """
        self.interface.setup_analog_sampling_sketch((0, 1), 500)
        self.interface.write_start_run()

    def stop_run(self):
        """
        """
        self.interface.write_stop_run()
        logger.info('Flushing the serial port...')
        data = self.interface.flush()



class PlasduinoMainWindow(MainWindow):

    """Mock main window for testing purposes.
    """

    PROJECT_NAME = PLASDUINO_PROJECT_NAME
    # pylint: disable=c-extension-no-member

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        #self.add_logger_tab()
