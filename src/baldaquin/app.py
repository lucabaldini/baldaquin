# Copyright (C) 2022--2025 the baldaquin team.
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

from typing import TYPE_CHECKING

from .__qt__ import QtCore
from .config import UserApplicationConfiguration
from .logging_ import logger

if TYPE_CHECKING:
    # We only need RunControl for type annotations, hence the if clause.
    from baldaquin.runctrl import RunControlBase


class UserApplicationBase:

    """Base class for user applications.
    """

    # pylint: disable=c-extension-no-member
    NAME = "User application"
    EVENT_HANDLER_CLASS = None
    CONFIGURATION_CLASS = None
    CONFIGURATION_FILE_PATH = None

    def __init__(self) -> None:
        """Constructor.
        """
        # pylint: disable=not-callable
        self.event_handler = self.EVENT_HANDLER_CLASS()
        # We should think about whether there is a more elegant way to do this.
        # Pass the user application to the child event handler? Use inheritance
        # rather than composition?
        self.event_handler.process_packet = self.process_packet
        self.configuration = self.CONFIGURATION_CLASS()
        if self.CONFIGURATION_FILE_PATH is not None:
            if self.CONFIGURATION_FILE_PATH.exists():
                self.configuration.update_from_file(self.CONFIGURATION_FILE_PATH)
            else:
                self.configuration.save(self.CONFIGURATION_FILE_PATH)

    def apply_configuration(self, configuration: UserApplicationConfiguration):
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
        logger.info(f"{self.__class__.__name__}.setup(): nothing to do...")

    def teardown(self) -> None:
        """Function called when the run control transitions from STOPPED to RESET.
        """
        logger.info(f"{self.__class__.__name__}.teardown(): nothing to do...")

    def start_run(self) -> None:
        """Start the event handler.
        """
        logger.info(f"Starting {self.NAME} user application...")
        self.event_handler.reset_statistics()
        QtCore.QThreadPool.globalInstance().start(self.event_handler)

    def stop_run(self) -> None:
        """Stop the event handler.
        """
        logger.info(f"Stopping {self.NAME} user application...")
        self.event_handler.stop()
        QtCore.QThreadPool.globalInstance().waitForDone()
        self.event_handler.flush_buffer()

    def pause(self) -> None:
        """Pause the event handler.
        """
        logger.info(f"Pausing {self.NAME} user application...")
        self.event_handler.stop()
        QtCore.QThreadPool.globalInstance().waitForDone()
        self.event_handler.flush_buffer()

    def resume(self) -> None:
        """Resume the event handler.
        """
        logger.info(f"Resuming {self.NAME} user application...")
        QtCore.QThreadPool.globalInstance().start(self.event_handler)

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.stop_run()

    def pre_start(self, run_control: "RunControlBase") -> None:
        """Hook that subclasses can use to perform any operation that needs to
        be done right before the application is stared (e.g., adding a custom
        sink to the underlying packet buffer.)
        """

    def post_stop(self, run_control: "RunControlBase") -> None:
        """Hook that subclasses can use to post-process the data collected in
        the run.
        """

    def process_packet(self, packet_data):
        """Optional hook for a user application to do something with the event data.
        """
