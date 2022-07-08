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

"""Data buffering.
"""

from collections import deque
import os

from loguru import logger


class CircularBuffer(deque):

    """
    """

    def __init__(self, file_path : str, max_length : int = None):
        """
        """
        super().__init__([], max_length)
        self.file_path = file_path

    def create_file(self):
        """
        """
        logger.info(f'Wiping out {self.file_path}')
        with open(self.file_path, 'w') as output_file:
            pass

    def write(self):
        """
        """
        if not len(self):
            return
        logger.debug(f'Writing {len(self)} packets to {self.file_path}...')
        with open(self.file_path, 'a') as output_file:
            while True:
                try:
                    output_file.write(f'{self.popleft()}\n')
                except IndexError:
                    break
