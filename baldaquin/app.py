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

from typing import Any

from loguru import logger

from baldaquin._qt import QtCore



class UserApplicationBase:

    """Base class for user applications.
    """

    #pylint: disable=c-extension-no-member
    EVENT_HANDLER_CLASS = None

    def __init__(self) -> None:
        """Constructor.
        """
        self.name = self.__class__.__name__
        self.event_handler = None

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
        logger.info(f'Starting application {self.__class__.__name__}')
        self.event_handler = self.EVENT_HANDLER_CLASS()
        self.event_handler.process_event = self.process_event
        self.event_handler.setup(file_path, **kwargs)
        QtCore.QThreadPool.globalInstance().start(self.event_handler)

    def stop(self) -> None:
        """Stop the event handler.
        """
        logger.info(f'Stopping application {self.__class__.__name__}')
        self.event_handler.stop()
        QtCore.QThreadPool.globalInstance().waitForDone()
        self.event_handler.flush_buffer()
        self.event_handler = None

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
