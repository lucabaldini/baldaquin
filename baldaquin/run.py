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

from baldaquin.timeline import Timeline


class RunControlStatus(Enum):

    """
    """

    RESET = auto()
    STOPPED = auto()
    RUNNING = auto()



class RunControl:

    """
    """

    NAME = None

    def __init__(self):
        """Constructor.
        """
        self._machine_id = self._read_machine_id()
        self._run_id = self._read_run_id()
        self._status = RunControlStatus.RESET
        self.timeline = Timeline()
        self.start_timestamp = None
        self.stop_timestamp = None

    def _read_machine_id(self):
        """
        """
        return 0

    def _read_run_id(self):
        """
        """
        return 0

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

    def _raise_invalid_transition(self, target):
        """
        """
        raise RuntimeError(f'Invalid state transition {self._status.name} -> {target.name}')

    def set_reset(self):
        """
        """
        target = RunControlStatus.RESET
        if self.is_stopped():
            self.teardown()
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def set_stopped(self):
        """
        """
        target = RunControlStatus.STOPPED
        if self.is_reset():
            self.setup()
        elif self.is_running():
            self.stop()
            self.stop_timestamp = self.timeline.latch()
            logger.info(f'{self.NAME} run control stopped on {self.stop_timestamp}')
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def set_running(self):
        """
        """
        target = RunControlStatus.RUNNING
        if self.is_stopped():
            self.start_timestamp = self.timeline.latch()
            logger.info(f'{self.NAME} run control started on {self.start_timestamp}')
            self._run_id += 1
            self._write_run_id()
            self._create_output_folder()
            self.start()
        else:
            self._raise_invalid_transition(target)
        self._status = target

    def elapsed_time(self):
        """
        """
        if self.start_timestamp is None:
            return None
        if self.stop_timestamp is None:
            return self.timeline.latch() - self.start_timestamp
        return self.stop_timestamp - self.start_timestamp

    def setup(self):
        """
        """
        raise NotImplementedError

    def teardown(self):
        """
        """
        raise NotImplementedError

    def start(self):
        """
        """
        raise NotImplementedError

    def stop(self):
        """
        """
        raise NotImplementedError



class RunControlNoOp(RunControl):

    """
    """

    NAME = 'NoOp'

    def setup(self):
        """
        """
        logger.info('Executing no-op setup()...')

    def teardown(self):
        """
        """
        logger.info('Executing no-op teardown()...')

    def start(self):
        """
        """
        logger.info('Executing no-op start()...')

    def stop(self):
        """
        """
        logger.info('Executing no-op stop()...')



if __name__ == '__main__':
    rc = RunControlNoOp()
    print(rc.is_reset())
    print(rc.elapsed_time())
    rc.set_stopped()
    rc.set_running()
    print(rc.elapsed_time())
    rc.set_stopped()
    print(rc.elapsed_time())
    print(rc.elapsed_time())
    rc.set_reset()
