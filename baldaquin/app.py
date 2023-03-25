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

"""User application framework.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from baldaquin.config import ConfigurationBase
from baldaquin._qt import QtCore



class UserApplicationBase:

    """Base class for user applications.
    """

    #pylint: disable=c-extension-no-member
    NAME = 'User application'
    EVENT_HANDLER_CLASS = None
    CONFIGURATION_CLASS = None
    CONFIGURATION_FILE_PATH = None

    def __init__(self) -> None:
        """Constructor.
        """
        self.event_handler = None
        self.configuration = self.CONFIGURATION_CLASS()
        if self.CONFIGURATION_FILE_PATH is not None:
            if self.CONFIGURATION_FILE_PATH.exists():
                self.configuration.update(self.CONFIGURATION_FILE_PATH)
            else:
                self.configuration.save(self.CONFIGURATION_FILE_PATH)

    def set_configuration(self, configuration : ConfigurationBase):
        """Set the configuration for the user application.
        """
        self.configuration = configuration
        if self.CONFIGURATION_FILE_PATH is not None:
            self.configuration.save(self.CONFIGURATION_FILE_PATH)
        self.configure()

    def configure(self):
        """Apply a given configuration to the user application.
        """
        raise NotImplementedError

    def setup(self) -> None:
        """Function called when the run control transitions from RESET to STOPPED.
        """
        logger.info(f'{self.__class__.__name__}.setup(): nothing to do...')

    def teardown(self) -> None:
        """Function called when the run control transitions from STOPPED to RESET.
        """
        logger.info(f'{self.__class__.__name__}.teardown(): nothing to do...')

    def start(self, file_path, **kwargs) -> None:
        """Start the event handler.

        .. warning::

           Note that we create a new handler every time, as earlier attempts to
           create the handler in the constructor and then start it multiple
           times seemed to trigger an error along the lines of:

           RuntimeError: Internal C++ object (MockEventHandler) already deleted.

           I am sure this deserves more study to make sure we are doing things
           correctly.
        """
        logger.info(f'Starting {self.NAME} user application...')
        self.event_handler = self.EVENT_HANDLER_CLASS()
        self.event_handler.process_event = self.process_event
        self.event_handler.setup(file_path, **kwargs)
        QtCore.QThreadPool.globalInstance().start(self.event_handler)

    def stop(self) -> None:
        """Stop the event handler.
        """
        logger.info(f'Stopping {self.NAME} user application...')
        self.event_handler.stop()
        QtCore.QThreadPool.globalInstance().waitForDone()
        self.event_handler.flush_buffer()
        self.event_handler = None

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
