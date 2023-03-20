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


"""Basic run control structure.
"""

from enum import Enum, auto
from datetime import datetime
from pathlib import Path

from loguru import logger

from baldaquin import BALDAQUIN_CONFIG, config_folder_path
from baldaquin.app import UserApplicationBase
from baldaquin.timeline import Timeline


class RunControlStatus(Enum):

    """Enum for the run control finite state machine possible states.
    """

    RESET = auto()
    STOPPED = auto()
    RUNNING = auto()



class AppNotLoadedError(RuntimeError):

    def __init__(self):
        """Constructor.
        """
        super().__init__('User application not loaded.')



class RunControlBase:

    """Run control class.
    """

    PROJECT_NAME = None

    def __init__(self):
        """Constructor.
        """
        self._test_stand_id = self._read_test_stand_id()
        logger.info(f'Test stand is is {self._test_stand_id}')
        self._run_id = self._read_run_id()
        self._status = RunControlStatus.RESET
        self.timeline = Timeline()
        self.start_timestamp = None
        self.stop_timestamp = None
        self._user_application = None

    def _config_file_path(self, file_name : str) -> Path:
        """Return the path to a generic configuration file.

        Arguments
        ---------
        file_name : str
            The file name.
        """
        return config_folder_path(self.PROJECT_NAME) / file_name

    def _test_stand_id_file_path(self) -> Path:
        """Return the path to the configuration file holding the test stand id.
        """
        return self._config_file_path('test_stand.cfg')

    def _run_id_file_path(self) -> Path:
        """Return the path to the configuration file holding the run id.
        """
        return self._config_file_path('run.cfg')

    def _read_config_file(self, default : int) -> int:
        """
        """
        pass

    def _write_config_file(self) -> int:
        """
        """
        pass

    def _read_test_stand_id(self, default : int = 101) -> int:
        """Read the test stand id from file.
        """
        file_path = self._test_stand_id_file_path()
        if not file_path.exists():
            logger.warning(f'Cannot find test-stand configuration file, creating a default one...')
            self._create_test_stand_id_file(default)
            return default
        logger.info(f'Reading test-stand id from {file_path}...')
        test_stand_id = int(file_path.read_text())
        return test_stand_id

    def _create_test_stand_id_file(self, test_stand_id : int) -> None:
        """Write a given test-stand id to file.
        """
        file_path = self._test_stand_id_file_path()
        logger.info(f'Writing test-stand id {test_stand_id} to {file_path}...')
        file_path.write_text(f'{test_stand_id}')

    def _read_run_id(self) -> int:
        """Read the run ID from the proper configuration file.
        """
        file_path = config_folder_path(self.PROJECT_NAME) / 'run.cfg'
        if not file_path.exists():
            logger.warning(f'Cannot find run id file, starting from zero...')
            return 0
        logger.info(f'Reading run id from {file_path}...')
        run_id = int(file_path.read_text())
        return run_id

    def _write_run_id(self):
        """
        """
        file_path = self._run_id_file_path()
        logger.info(f'Writing run id {self._run_id} to {file_path}...')
        file_path.write_text(f'{run_id}')

    def _increment_run_id(self):
        """
        """
        self._run_id += 1
        self._write_run_id()

    def set_user_application(self, app):
        """
        """
        if not isinstance(app, UserApplicationBase):
            raise RuntimeError('Invalid user application')
        self._user_application = app

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
            logger.info(f'Run Control stopped on {self.stop_timestamp}')
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
            logger.info(f'Run Control started on {self.start_timestamp}')
            self._increment_run_id()
            self._create_output_folder()
            file_path = f'testdata_{self._run_id:05d}.dat'
            self._user_application.start(file_path)
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
