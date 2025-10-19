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

"""Profiling facilities.
"""

import time
from functools import wraps

from .logging_ import logger


def timing(func):
    """Small decorator to time a generic function.
    """
    @wraps(func)
    def wrap(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        logger.debug(f"Running time for {func.__name__}(): {time.time() - start_time:.6f} s")
        return result
    return wrap
