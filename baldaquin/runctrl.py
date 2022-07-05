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


"""Basic run control structure.
"""

from enum import Enum, auto
from datetime import datetime

from loguru import logger

from baldaquin.app import UserApplicationBase
from baldaquin.timeline import Timeline


class RunControlStatus(Enum):

    """Enum for the run control finite state machine possible states.
    """

    RESET = auto()
    STOPPED = auto()
    RUNNING = auto()



class RunControl:

    """Run control class.
    """

    NAME = 'Default run control'

    def __init__(self):
        """Constructor.
        """
        self._machine_id = self._read_machine_id()
        self._run_id = self._read_run_id()
        self._status = RunControlStatus.RESET
        self.timeline = Timeline()
        self.start_timestamp = None
        self.stop_timestamp = None
        self._user_application = None

    def set_user_application(self, app):
        """
        """
        if not isinstance(app, UserApplicationBase):
            raise RuntimeError('Invalid user application')
        self._user_application = app

    def _read_machine_id(self):
        """
        """
        return 0

    def _read_run_id(self):
        """
        """
        return 0

    def _increment_run_id(self):
        """
        """
        pass

    def _write_run_id(self):
        """
        """
        pass

    def _create_output_folder(self):
        """
        """
        pass

    def is_reset(self) -> bool:
        """Return True if the run control is reset.
        """
        return self._status == RunControlStatus.RESET

    def is_stopped(self) -> bool:
        """Return True if the run control is stopped.
        """
        return self._status == RunControlStatus.STOPPED

    def is_running(self) -> bool:
        """Return True if the run control is running.
        """
        return self._status == RunControlStatus.RUNNING

    def _raise_invalid_transition(self, target : RunControlStatus) -> None:
        """
        """
        raise RuntimeError(f'Invalid state transition {self._status.name} -> {target.name}')

    def _raise_user_application_not_loaded(self) -> None:
        """
        """
        raise RuntimeError('User application not loaded...')

    def set_reset(self) -> None:
        """
        """
        if self._user_application is None:
            self._raise_user_application_not_loaded()
        target = RunControlStatus.RESET
        if self.is_stopped():
            self._user_application.teardown()
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def set_stopped(self) -> None:
        """
        """
        if self._user_application is None:
            self._raise_user_application_not_loaded()
        target = RunControlStatus.STOPPED
        if self.is_reset():
            self._user_application.setup()
        elif self.is_running():
            self._user_application.stop()
            self.stop_timestamp = self.timeline.latch()
            logger.info(f'{self.NAME} stopped on {self.stop_timestamp}')
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def set_running(self) -> None:
        """
        """
        if self._user_application is None:
            self._raise_user_application_not_loaded()
        target = RunControlStatus.RUNNING
        if self.is_stopped():
            self.start_timestamp = self.timeline.latch()
            logger.info(f'{self.NAME} started on {self.start_timestamp}')
            self._run_id += 1
            self._write_run_id()
            self._create_output_folder()
            self._user_application.start()
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def elapsed_time(self) -> float:
        """
        """
        if self.start_timestamp is None:
            return None
        if self.stop_timestamp is None:
            return self.timeline.latch() - self.start_timestamp
        return self.stop_timestamp - self.start_timestamp
