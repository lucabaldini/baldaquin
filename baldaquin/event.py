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

"""Event handler.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import struct
import time
from typing import Any

from baldaquin.buf import CircularBuffer
from baldaquin._qt import QtCore



class EventHandlerBase(QtCore.QRunnable):

    # pylint: disable=c-extension-no-member

    """Base class for an event handler.

    This is an abstract base class inheriting from ``QtCore.QRunnable``, owning
    a data buffer that can be used to cache data, and equipped with a binary flag
    that allows for syncronization.

    Arguments
    ---------
    file_path : str
        The path to the output file.

    buffer_class : type
        The class to be used to instantiate the event buffer object.

    kwargs : dict
        Keyword arguents for the data buffer creation.
    """

    def __init__(self, file_path : str, buffer_class : type = CircularBuffer, **kwargs) -> None:
        """Constructor.
        """
        super().__init__()
        self.buffer = buffer_class(file_path, **kwargs)
        self.__running = False

    def stop(self) -> None:
        """Stop the event handler.
        """
        self.__running = False

    def run(self) -> None:
        """Overloaded QRunnable method.
        """
        self.__running = True
        while self.__running:
            self.buffer.put_item(self.process_event())

    def process_event(self) -> Any:
        """Process a single event (must be overloaded in derived classes).
        """
        raise NotImplementedError
