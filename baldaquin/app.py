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

from baldaquin.buf import CircularBuffer
from baldaquin._qt import QtCore



class UserApplicationBase(QtCore.QRunnable):

    """Base class for user applications.
    """

    BUFFER_CLASS = CircularBuffer

    def __init__(self, file_path : str, **kwargs) -> None:
        """Constructor.
        """
        super().__init__()
        self.buffer = BUFFER_CLASS(file_path, **kwargs)
        self.__running = False

    def setup(self) -> None:
        """Function called when the run control transitions from RESET to STOPPED.
        """
        logger.info(f'{self.__class__.__name__}.setup(): nothing to do...')

    def teardown(self) -> None:
        """Function called when the run control transitions from STOPPED to RESET.
        """
        logger.info(f'{self.__class__.__name__}.teardown(): nothing to do...')

    def run(self) -> None:
        """Overloaded QRunnable method.
        """
        self.__running = True
        while self.__running:
            self.buffer.put_item(self.process_event())

    def start(self) -> None:
        """Start the event handler.
        """
        self.run()

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False
        # Flush the buffer?

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
