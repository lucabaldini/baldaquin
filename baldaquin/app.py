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



class UserApplicationBase:

    """Base class for user applications.
    """

    def setup(self) -> None:
        """Function called when the run control transitions from RESET to STOPPED.
        """
        logger.info('Nothing to do at setup()...')

    def teardown(self) -> None:
        """Function called when the run control transitions from STOPPED to RESET.
        """
        logger.info('Nothing to do at teardown()...')

    def start(self) -> None:
        """Function called when the run control transitions from STOPPED to RUNNING.
        """
        raise NotImplementedError('start() not implemented')

    def stop(self) -> None:
        """Function called when the run control transitions from RUNNING to STOPPED.
        """
        raise NotImplementedError('stop() not implemented')



class UserAppNoOp(UserApplicationBase):

    """Simple do-nothing application for test purposes.
    """

    NAME = 'NoOp user application'

    def setup(self) -> None:
        """Overloaded do-nothing method.
        """
        logger.info('Executing no-op setup()...')

    def teardown(self) -> None:
        """Overloaded do-nothing method.
        """
        logger.info('Executing no-op teardown()...')

    def start(self) -> None:
        """Overloaded do-nothing method.
        """
        logger.info('Executing no-op start()...')

    def stop(self) -> None:
        """Overloaded do-nothing method.
        """
        logger.info('Executing no-op stop()...')