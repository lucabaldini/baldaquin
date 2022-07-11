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

from loguru import logger
from typing import Any

from baldaquin._qt import QtCore



class UserApplicationBase:

    """Base class for user applications.
    """

    EVENT_HANDLER_CLASS = None

    def __init__(self) -> None:
        """Constructor.
        """
        self.pool = QtCore.QThreadPool.globalInstance()
        self.event_handler = self.EVENT_HANDLER_CLASS()
        self.event_handler.process_event = self.process_event

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
        """
        logger.info(f'Starting application {self.__class__.__name__}')
        self.event_handler.setup(file_path, **kwargs)
        self.pool.start(self.event_handler)

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.event_handler.stop()
        self.pool.waitForDone()
        self.event_handler.flush_buffer()

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
