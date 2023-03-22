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
from pathlib import Path

from loguru import logger

from baldaquin import config_folder_path, data_folder_path
from baldaquin.app import UserApplicationBase
from baldaquin.timeline import Timeline



class FsmState(Enum):

    """Enum for the run control finite state machine possible states.
    """

    RESET = auto()
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()



class InvalidFsmTransitionError(RuntimeError):

    """RuntimeError subclass to signal an invalid FSM transition.
    """

    def __init__(self, src, dest):
        """Constructor.
        """
        super().__init__(f'Invalid FSM transition {src.name} -> {dest.name}.')



class FiniteStateMachine:

    """Definition of the finite-state machine (FSM) underlying the run control.

    The finite state machine has a unique _state class member, and all the logic
    embedded to manage the transitions between its different values.

    This is an abstract class, and subclasses are ultimately responsible for
    reimplementing all the virtual methods, i.e.,

    * setup(), called in the RESET -> STOPPED transition;
    * teardown(), called in the STOPPED -> RESET transition;
    * start_run(), called in the STOPPED -> RUNNING transition;
    * stop_run(), called in the RUNNING -> STOPPED transition;
    * pause(), called in the RUNNING -> PAUSED transition;
    * resume(), called in the PAUSED -> RUNNING transition;
    * stop(), called in the PAUSED -> STOPPED transition.

    The interaction with concrete instances of subclasses happens through the
    four methods that set the FSM state, calling the proper hook:

    * set_reset();
    * set_stopped();
    * set_running();
    * set_paused().
    """

    def __init__(self) -> None:
        """Constructor.
        """
        self._state = FsmState.RESET

    def is_reset(self) -> bool:
        """Return True if the run control is reset.
        """
        return self._state == FsmState.RESET

    def is_stopped(self) -> bool:
        """Return True if the run control is stopped.
        """
        return self._state == FsmState.STOPPED

    def is_running(self) -> bool:
        """Return True if the run control is running.
        """
        return self._state == FsmState.RUNNING

    def is_paused(self) -> bool:
        """Return True if the run control is paused.
        """
        return self._state == FsmState.PAUSED

    def setup(self) -> None:
        """Method called in the RESET -> STOPPED transition.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Method called in the STOPPED -> RESET transition.
        """
        raise NotImplementedError

    def start_run(self) -> None:
        """Method called in the STOPPED -> RUNNING transition.
        """
        raise NotImplementedError

    def stop_run(self) -> None:
        """Method called in the RUNNING -> STOPPED transition.
        """
        raise NotImplementedError

    def pause(self) -> None:
        """Method called in the RUNNING -> PAUSED transition.
        """
        raise NotImplementedError

    def resume(self) -> None:
        """Method called in the PAUSED -> RUNNING transition.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """Method called in the PAUSED -> STOPPED transition.
        """
        raise NotImplementedError

    def set_reset(self) -> None:
        """Set the FST in the RESET state.
        """
        target_state = FsmState.RESET
        if self.is_stopped():
            self.teardown()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self._state = target_state

    def set_stopped(self) -> None:
        """Set the FST in the STOPPED state.
        """
        target_state = FsmState.STOPPED
        if self.is_reset():
            self.setup()
        elif self.is_running():
            self.stop_run()
        elif self.is_paused():
            self.stop()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self._state = target_state

    def set_running(self) -> None:
        """Set the FST in the RUNNING state.
        """
        target_state = FsmState.RUNNING
        if self.is_stopped():
            self.start_run()
        elif self.is_paused():
            self.resume()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self._state = target_state

    def set_paused(self) -> None:
        """Set the FST in the PAUSED state.
        """
        target_state = FsmState.PAUSED
        if self.is_running():
            self.pause()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self._state = target_state



class AppNotLoadedError(RuntimeError):

    """RuntimeError subclass to signal that the run control has no user application loaded.
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__('User application not loaded.')



class RunControlBase(FiniteStateMachine):

    """Run control class.
    """

    PROJECT_NAME = None

    def __init__(self):
        """Constructor.
        """
        super().__init__()
        self._test_stand_id = self._read_test_stand_id()
        self._run_id = self._read_run_id()
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

    def data_folder_path(self) -> Path:
        """Return the path to the data folder for the current run.
        """
        folder_name = f'{self._test_stand_id:04d}_{self._run_id:06d}'
        return data_folder_path(self.PROJECT_NAME) / folder_name

    def _file_name_base(self, label : str, extension : str) -> str:
        """Generic function implementing a file name factory, given the
        test stand and the run ID.

        Arguments
        ---------
        label : str
            A text label to attach to the file name.

        extension : str
            The file extension
        """
        return f'{self._test_stand_id:04d}_{self._run_id:05d}_{label}.{extension}'

    def data_file_name(self) -> str:
        """Return the current data file name.

        Note that RunControlBase subclasses can overload this if a different
        naming convention is desired.
        """
        return self._file_name_base('data', 'dat')

    def data_file_path(self) -> Path:
        """Return the current
        """
        return self.data_folder_path() / self.data_file_name()

    def log_file_name(self):
        """Return the current log file name.

        Note that RunControlBase subclasses can overload this if a different
        naming convention is desired.
        """
        return self._file_name_base('run', 'log')

    def log_file_path(self) -> Path:
        """Return the current
        """
        return self.data_folder_path() / self.log_file_name()

    @staticmethod
    def _read_config_file(file_path : Path, default : int) -> int:
        """Read a single integer value from a given configuration file.

        If the file is not found, a new one is created, holding the default value,
        and the latter is returned.

        Arguments
        ---------
        file_path : Path
            The path to the configuration file.

        default : int
            The default value, to be used if the file is not found.
        """
        if not file_path.exists():
            logger.warning(f'Configuration file {file_path} not found, creating one...')
            RunControlBase._write_config_file(file_path, default)
            return default
        logger.info(f'Reading configuration file {file_path}...')
        value = int(file_path.read_text())
        logger.info(f'Done, {value} found.')
        return value

    @staticmethod
    def _write_config_file(file_path : Path, value : int) -> None:
        """Write a single integer value to a given configuration file.

        Arguments
        ---------
        file_path : Path
            The path to the configuration file.

        value : int
            The value to be written.
        """
        logger.info(f'Writing {value} to config file {file_path}...')
        file_path.write_text(f'{value}')

    def _read_test_stand_id(self, default : int = 101) -> int:
        """Read the test stand id from the proper configuration file.
        """
        return self._read_config_file(self._test_stand_id_file_path(), default)

    def _read_run_id(self) -> int:
        """Read the run ID from the proper configuration file.
        """
        return self._read_config_file(self._run_id_file_path(), 0)

    def _write_run_id(self) -> None:
        """Write the current run ID to the proper configuration file.
        """
        self._write_config_file(self._run_id_file_path(), self._run_id)

    def _increment_run_id(self) -> None:
        """Increment the run ID by one unit and update the corresponding
        configuration file.
        """
        self._run_id += 1
        self._write_run_id()

    def _create_data_folder(self) -> None:
        """Create the folder for the output data.
        """
        folder_path = self.data_folder_path()
        logger.info(f'Creating output data folder {folder_path}')
        Path.mkdir(folder_path)

    def elapsed_time(self) -> float:
        """Return the elapsed time.
        """
        if self.start_timestamp is None:
            return None
        if self.stop_timestamp is None:
            return self.timeline.latch() - self.start_timestamp
        return self.stop_timestamp - self.start_timestamp

    def load_user_application(self, app : UserApplicationBase) -> None:
        """Set the user application to be run.
        """
        if not self.is_reset():
            raise RuntimeError(f'Cannot load a user application in the {self._state.name} state')
        if not isinstance(app, UserApplicationBase):
            raise RuntimeError(f'Invalid user application of type {type(app)}')
        self._user_application = app

    def _check_user_application(self) -> None:
        """Make sure we have a valid use application loaded, and raise an
        AppNotLoadedError if that is not the case.
        """
        if self._user_application is None:
            raise AppNotLoadedError

    def setup(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()
        self._user_application.setup()

    def teardown(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()
        self._user_application.teardown()

    def start_run(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()
        self._increment_run_id()
        self._create_data_folder()
        self.start_timestamp = self.timeline.latch()
        logger.info(f'Run Control started on {self.start_timestamp}')
        self._user_application.start(self.data_file_path())

    def stop_run(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()
        self._user_application.stop()
        self.stop_timestamp = self.timeline.latch()
        logger.info(f'Run Control stopped on {self.stop_timestamp}')

    def pause(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()

    def resume(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()

    def stop(self) -> None:
        """Overloaded FiniteStateMachine method.
        """
        self._check_user_application()
