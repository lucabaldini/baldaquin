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


"""Basic run control structure.
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import __version__
from .__qt__ import QtCore
from .app import UserApplicationBase
from .config import UserApplicationConfiguration
from .env import BALDAQUIN_ENCODING, config_folder_path, data_folder_path
from .event import PacketStatistics
from .logging_ import logger, setup_logger, start_file_logging
from .timeline import Timeline, Timestamp


class FsmState(Enum):

    """Enum for the run control finite state machine possible states.
    """

    RESET = "Reset"
    STOPPED = "Stopped"
    RUNNING = "Running"
    PAUSED = "Paused"


class InvalidFsmTransitionError(RuntimeError):

    """RuntimeError subclass to signal an invalid FSM transition.
    """

    def __init__(self, src, dest):
        """Constructor.
        """
        super().__init__(f"Invalid FSM transition {src.name} -> {dest.name}.")


class FiniteStateMachineLogic:

    """Class encapsulating the basic logic of the run control finite-state machine.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        self._state = FsmState.RESET

    def state(self) -> FsmState:
        """Return the state of the FSM.
        """
        return self._state

    def set_state(self, state: FsmState) -> None:
        """Set the state of the FSM.
        """
        self._state = state

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
        """Method called in the ``RESET`` -> ``STOPPED`` transition.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Method called in the ``STOPPED`` -> ``RESET`` transition.
        """
        raise NotImplementedError

    def start_run(self) -> None:
        """Method called in the ``STOPPED`` -> ``RUNNING`` transition.
        """
        raise NotImplementedError

    def stop_run(self) -> None:
        """Method called in the ``RUNNING`` -> ``STOPPED`` transition.
        """
        raise NotImplementedError

    def pause(self) -> None:
        """Method called in the ``RUNNING`` -> ``PAUSED`` transition.
        """
        raise NotImplementedError

    def resume(self) -> None:
        """Method called in the ``PAUSED -> ``RUNNING`` transition.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """Method called in the ``PAUSED`` -> ``STOPPED`` transition.
        """
        raise NotImplementedError

    def force_reset(self) -> None:
        """Go through all the necessary transitions to bring the FSM from the current
        state all the way to the ``RESET`` state.

        This is used, e.g., when the GUI is closed abruptly from the top-right cross
        and we still need to stop the data acquisition and put the hardware in a
        secure state before we actually shut everything down.
        """
        # If the run control is in either the RUNNING or PAUSED states, we first
        # need to transition to STOPPED.
        if self.is_running():
            self.stop_run()
        elif self.is_paused():
            self.stop()
        # At this point the status is STOPPED, and we just have to call teardown().
        if self.is_stopped():
            self.teardown()
        # And if the thing was in the RESET state to start with, then we're good.

    def set_reset(self) -> None:
        """Set the FSM in the ``RESET`` state.

        An :class:`InvalidFsmTransitionError <baldaquin.runctrl.InvalidFsmTransitionError>`
        exception is raised if the FSM is not in the ``STOPPED`` state.
        """
        target_state = FsmState.RESET
        if self.is_stopped():
            self.teardown()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self.set_state(target_state)

    def set_stopped(self) -> None:
        """Set the FSM in the ``STOPPED`` state.

        An :class:`InvalidFsmTransitionError <baldaquin.runctrl.InvalidFsmTransitionError>`
        exception is raised if the FSM is not in either the ``RESET``, ``RUNNING``
        or ``PAUSED`` state.
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
        self.set_state(target_state)

    def set_running(self) -> None:
        """Set the FSM in the ``RUNNING`` state.

        An :class:`InvalidFsmTransitionError <baldaquin.runctrl.InvalidFsmTransitionError>`
        exception is raised if the FSM is not in either the ``STOPPED`` or ``PAUSED`` state.
        """
        target_state = FsmState.RUNNING
        if self.is_stopped():
            self.start_run()
        elif self.is_paused():
            self.resume()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self.set_state(target_state)

    def set_paused(self) -> None:
        """Set the FSM in the ``PAUSED`` state.

        An :class:`InvalidFsmTransitionError <baldaquin.runctrl.InvalidFsmTransitionError>`
        exception is raised if the FSM is not in either the ``RUNNING`` state.
        """
        target_state = FsmState.PAUSED
        if self.is_running():
            self.pause()
        else:
            raise InvalidFsmTransitionError(self._state, target_state)
        self.set_state(target_state)


class FiniteStateMachineBase(QtCore.QObject, FiniteStateMachineLogic):

    """Definition of the finite-state machine (FSM) underlying the run control.

    This is inheriting from FiniteStateMachineLogic and overloading the set_state()
    hook, so that a state_changed signal is emitted whenever the state is changed.
    (Note that, in order to do this, we also have to overload the constructor in
    order for the underlying QObject structure to be properly initialized.)
    """

    # pylint: disable=c-extension-no-member, abstract-method
    state_changed = QtCore.Signal(FsmState)

    def __init__(self) -> None:
        """Overloaded constructor.
        """
        QtCore.QObject.__init__(self)
        FiniteStateMachineLogic.__init__(self)

    def set_state(self, state: FsmState) -> None:
        """Set the state of the FSM and emit a ``state_changed()`` signal with the
        proper state after the change.
        """
        self._state = state
        self.state_changed.emit(self._state)


class AppNotLoadedError(RuntimeError):

    """RuntimeError subclass to signal that the run control has no user application loaded.
    """

    def __init__(self):
        """Constructor.
        """
        super().__init__("User application not loaded.")


@dataclass
class RunReport:

    """Small container class describing a run report.
    """

    baldaquin_version: str
    test_stand_id: int
    run_id: int
    start_timestamp: Timestamp
    stop_timestamp: Timestamp
    project_name: str
    application_name: str
    statistics: PacketStatistics

    _VERSION = 1
    _VERSION_FIELD_NAME = "report_version"

    def to_dict(self):
        """Serialization.
        """
        _dict = {self._VERSION_FIELD_NAME: self._VERSION}
        _dict.update(self.__dict__)
        for key in ("start_timestamp", "stop_timestamp", "statistics"):
            _dict[key] = _dict[key].to_dict()
        return _dict

    @classmethod
    def from_dict(cls, **kwargs) -> "RunReport":
        """Deserialization.
        """
        _ = kwargs.pop(cls._VERSION_FIELD_NAME)
        for key in ("start_timestamp", "stop_timestamp"):
            kwargs.update({key: Timestamp.from_dict(**kwargs[key])})
        for key in ("statistics", ):
            kwargs.update({key: PacketStatistics.from_dict(**kwargs[key])})
        return cls(**kwargs)

    def dumps(self, indent: int = 4) -> str:
        """Return a text representation of the object in json format.
        """
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, file_path: str) -> None:
        """Save the report to file.
        """
        logger.info(f"Writing run report to {file_path}...")
        with open(file_path, "w", encoding=BALDAQUIN_ENCODING) as output_file:
            output_file.write(self.dumps())

    @classmethod
    def load(cls, file_path):
        """Load the report from file.
        """
        logger.info(f"Loading run report from {file_path}...")
        with open(file_path, encoding=BALDAQUIN_ENCODING) as input_file:
            return cls.from_dict(**json.load(input_file))


class RunControlBase(FiniteStateMachineBase):

    """Run control class.

    Derived classes need to set the ``_PROJECT_NAME`` class member (this controls
    the placement of the output files) and, optionally ``_DEFAULT_REFRESH_INTERVAL``
    as well.

    Arguments
    ---------
    refresh_interval : int
        The timeout interval (in ms) for the underlying refresh QTimer object
        updating the information on the control GUI as the data taking proceeds.
    """

    # pylint: disable=c-extension-no-member, too-many-instance-attributes, too-many-public-methods
    _PROJECT_NAME = None
    _DEFAULT_REFRESH_INTERVAL = 750

    run_id_changed = QtCore.Signal(int)
    user_application_loaded = QtCore.Signal(UserApplicationBase)
    uptime_updated = QtCore.Signal(float)
    event_handler_stats_updated = QtCore.Signal(PacketStatistics, float)

    def __init__(self, refresh_interval: int = _DEFAULT_REFRESH_INTERVAL) -> None:
        """Constructor.
        """
        if self._PROJECT_NAME is None:
            msg = f"{self.__class__.__name__} needs to be subclassed, and _PROJECT_NAME set."
            raise RuntimeError(msg)
        super().__init__()
        self._test_stand_id = self._read_test_stand_id()
        self._run_id = self._read_run_id()
        self.timeline = Timeline()
        self.start_timestamp = None
        self.stop_timestamp = None
        self._user_application = None
        self._log_file_handler_id = None
        self._update_timer = QtCore.QTimer()
        self.set_refresh_interval(refresh_interval)
        self._update_timer.timeout.connect(self.update_stats)

    def test_stand_id(self) -> int:
        """Return the test-stand ID.
        """
        return self._test_stand_id

    def run_id(self) -> int:
        """Return the current run ID.
        """
        return self._run_id

    def set_refresh_interval(self, refresh_interval: int) -> None:
        """Set the timeout for the underlying refresh QTimer object.

        Arguments
        ---------
        refresh_interval : int
            The refresh interval in ms.
        """
        self._update_timer.setInterval(refresh_interval)

    def _config_file_path(self, file_name: str) -> Path:
        """Return the path to a generic configuration file.

        Arguments
        ---------
        file_name : str
            The file name.
        """
        return config_folder_path(self._PROJECT_NAME) / file_name

    def _test_stand_id_file_path(self) -> Path:
        """Return the path to the configuration file holding the test stand id.
        """
        return self._config_file_path("test_stand.cfg")

    def _run_id_file_path(self) -> Path:
        """Return the path to the configuration file holding the run id.
        """
        return self._config_file_path("run.cfg")

    def _file_name_base(self, label: str = None, extension: str = None) -> str:
        """Generic function implementing a file name factory, given the
        test stand and the run ID.

        Arguments
        ---------
        label : str
            A text label to attach to the file name.

        extension : str
            The file extension
        """
        file_name = f"{self._test_stand_id:04d}_{self._run_id:06d}"
        if label is not None:
            file_name = f"{file_name}_{label}"
        if extension is not None:
            file_name = f"{file_name}.{extension}"
        return file_name

    def data_folder_path(self) -> Path:
        """Return the path to the data folder for the current run.
        """
        return data_folder_path(self._PROJECT_NAME) / self._file_name_base()

    def output_file_path_base(self) -> Path:
        """Return the base pattern for all the output files.

        This is use to pass the message about where to write output files to
        user applications.
        """
        return self.data_folder_path() / self._file_name_base()

    def data_file_name(self) -> str:
        """Return the file name for the current data file.

        Note that RunControlBase subclasses can overload this if a different
        naming convention is desired.
        """
        return self._file_name_base("data", "dat")

    def data_file_path(self) -> Path:
        """Return the path to the current data file.
        """
        return self.data_folder_path() / self.data_file_name()

    def log_file_name(self):
        """Return the file name for the current log file.

        Note that RunControlBase subclasses can overload this if a different
        naming convention is desired.
        """
        return self._file_name_base("run", "log")

    def log_file_path(self) -> Path:
        """Return the path to the current log file.
        """
        return self.data_folder_path() / self.log_file_name()

    def config_file_name(self) -> str:
        """Return the file name for the current configuration.
        """
        return self._file_name_base("config", "json")

    def config_file_path(self) -> Path:
        """Return the path to the current configuration.
        """
        return self.data_folder_path() / self.config_file_name()

    def report_file_name(self) -> str:
        """Return the file name for the current run report.
        """
        return self._file_name_base("report", "json")

    def report_file_path(self) -> Path:
        """Return the path to the current run report.
        """
        return self.data_folder_path() / self.report_file_name()

    @staticmethod
    def _read_config_file(file_path: Path, default: int) -> int:
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
            logger.warning(f"Configuration file {file_path} not found, creating one...")
            RunControlBase._write_config_file(file_path, default)
            return default
        logger.info(f"Reading configuration file {file_path}...")
        value = int(file_path.read_text())
        logger.info(f"Done, {value} found.")
        return value

    @staticmethod
    def _write_config_file(file_path: Path, value: int) -> None:
        """Write a single integer value to a given configuration file.

        Arguments
        ---------
        file_path : Path
            The path to the configuration file.

        value : int
            The value to be written.
        """
        logger.info(f"Writing {value} to config file {file_path}...")
        file_path.write_text(f"{value}")

    def _read_test_stand_id(self, default: int = 101) -> int:
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
        self.run_id_changed.emit(self._run_id)
        self._write_run_id()

    def _create_data_folder(self) -> None:
        """Create the folder for the output data.
        """
        folder_path = self.data_folder_path()
        logger.info(f"Creating output data folder {folder_path}")
        Path.mkdir(folder_path)

    def elapsed_time(self) -> float:
        """Return the elapsed time.

        The precise semantics of this function is:

        * is the run control is either running or paused, return the elapsed time
          since the start of the run;
        * if both the start and the stop timestamps are not None, then return the
          total elapsed time in the last run;
        * if both of the above fail, then return None.
        """
        if self.is_running() or self.is_paused():
            return self.timeline.latch() - self.start_timestamp
        try:
            return self.stop_timestamp - self.start_timestamp
        except TypeError:
            return None

    def update_stats(self):
        """Signal the proper updates to the run statistics.
        """
        elapsed_time = self.elapsed_time()
        statistics = self._user_application.event_handler.statistics()
        try:
            event_rate = statistics.packets_processed / elapsed_time
        except TypeError:
            event_rate = 0.
        self.uptime_updated.emit(elapsed_time)
        self.event_handler_stats_updated.emit(statistics, event_rate)

    def write_run_report(self) -> None:
        """Write an end-of-run report in the output folder.
        """
        report = RunReport(__version__, self._test_stand_id, self._run_id, self.start_timestamp,
                           self.stop_timestamp, self._PROJECT_NAME,
                           self._user_application.__class__.__name__,
                           self._user_application.event_handler.statistics())
        report.save(self.report_file_path())

    def load_user_application(self, user_application: UserApplicationBase) -> None:
        """Set the user application to be run.
        """
        logger.info("Loading user application...")
        if not self.is_reset():
            raise RuntimeError(f"Cannot load a user application in the {self.state().name} state")
        if not isinstance(user_application, UserApplicationBase):
            raise RuntimeError(f"Invalid user application of type {type(user_application)}")
        self._user_application = user_application
        # Mind we want to set the state to STOPPED before we emit the user_application_loaded()
        # signal, in order to avoid triggering invalid transtions downstream.
        self.set_stopped()
        self.user_application_loaded.emit(user_application)

    def _check_user_application(self) -> None:
        """Make sure we have a valid use application loaded, and raise an
        AppNotLoadedError if that is not the case.
        """
        if self._user_application is None:
            raise AppNotLoadedError

    def configure_user_application(self, configuration: UserApplicationConfiguration) -> None:
        """Apply a given configuration to the current user application.
        """
        self._check_user_application()
        logger.info("Configuring user application...")
        self._user_application.apply_configuration(configuration)

    def setup(self) -> None:
        """Overloaded method.
        """
        self._check_user_application()
        self._user_application.setup()

    def teardown(self) -> None:
        """Overloaded method.
        """
        self._check_user_application()
        self._user_application.teardown()

    def start_run(self) -> None:
        """Overloaded method.
        """
        # Note that configure_user_application() has been called before this.
        # We should think carefully about whether we're doing the right thing...
        self._check_user_application()
        self._increment_run_id()
        self._create_data_folder()
        # Apply all the necessary configurations. Note this needs to happen after
        # the run ID has been incremented, so that the log file points to the
        # right place.
        configuration = self._user_application.configuration
        logger.info(f"Applying configuration...\n{configuration}")
        logger.info("Configuring logging...")
        section = configuration.logging_section()
        setup_logger(section.value("terminal_level"))
        self._log_file_handler_id = start_file_logging(self.log_file_path(),
                                                       section.value("file_level"))
        logger.info("Configuring packet buffering...")
        section = configuration.buffering_section()
        flush_size = section.value("flush_size")
        flush_timeout = section.value("flush_timeout")
        self._user_application.event_handler.configure_buffer(flush_size, flush_timeout)
        configuration.save(self.config_file_path())
        # Configuration applied and written, we might move on.
        self.start_timestamp = self.timeline.latch()
        self.stop_timestamp = None
        logger.info(f"Run Control started on {self.start_timestamp}")
        self._user_application.event_handler.set_primary_sink(self.data_file_path())
        self._user_application.pre_start(self)
        self._user_application.start_run()
        self._update_timer.start()
        self.update_stats()

    def stop_run(self) -> None:
        """Overloaded method.
        """
        self._check_user_application()
        self._update_timer.stop()
        self._user_application.stop_run()
        self._user_application.post_stop(self)
        self.stop_timestamp = self.timeline.latch()
        logger.info(f"Run Control stopped on {self.stop_timestamp}")
        logger.info(f"Total elapsed time: {self.elapsed_time():6f} s.")
        if self._log_file_handler_id is not None:
            logger.remove(self._log_file_handler_id)
        self._log_file_handler_id = None
        self._user_application.event_handler.disconnect_sinks()
        self.write_run_report()
        self.update_stats()

    def pause(self) -> None:
        """Overloaded method.
        """
        self._check_user_application()
        self._user_application.pause()

    def resume(self) -> None:
        """Overloaded method.
        """
        self._check_user_application()
        self._user_application.resume()

    def stop(self) -> None:
        """Overloaded method.
        """
        self.stop_run()
