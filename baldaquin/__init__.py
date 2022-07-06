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


"""System-wide facilities.
"""

import os
import sys

from loguru import logger


BALDAQUIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
BALDAQUIN_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def __join(*args, base_folder : str = BALDAQUIN_ROOT) -> str:
    """Path concatenation relative to the base package folder (avoids some typing).
    """
    return os.path.join(base_folder, *args)


# Basic package structure.
BALDAQUIN_CORE = __join('core')
BALDAQUIN_GRAPHICS = __join('graphics')
BALDAQUIN_ICONS = __join('icons', base_folder=BALDAQUIN_GRAPHICS)
BALDAQUIN_SKINS = __join('skins', base_folder=BALDAQUIN_GRAPHICS)
BALDAQUIN_DOCS = __join('docs', base_folder=BALDAQUIN_BASE)
BALDAQUIN_DOCS_STATIC = __join('_static', base_folder=BALDAQUIN_DOCS)
BALDAQUIN_TESTS = __join('test', base_folder=BALDAQUIN_BASE)

try:
    BALDAQUIN_DATA = os.environ['BALDAQUIN_DATA']
except KeyError:
    BALDAQUIN_DATA = os.path.join(os.path.expanduser('~'), 'baldaquindata')
if not os.path.exists(BALDAQUIN_DATA):
    os.makedirs(BALDAQUIN_DATA)



DEFAULT_LOGURU_HANDLER = dict(
    sink=sys.stderr, colorize=True, format=">>> <level>{message}</level>"
    )


def config_logger(file_path=None, extra=None):
    """
    """
    handlers = [DEFAULT_LOGURU_HANDLER]
    if file_path is not None:
        handlers.append(dict(sink=file_path, enqueue=True, serialize=True))
    logger.configure(handlers=handlers, levels=None, extra=extra)
