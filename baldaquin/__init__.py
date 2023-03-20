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
from pathlib import Path
import sys

from loguru import logger


# Basic package structure.
BALDAQUIN_ROOT = Path(__file__).parent
BALDAQUIN_BASE = BALDAQUIN_ROOT.parent
BALDAQUIN_CORE = BALDAQUIN_ROOT / 'core'
BALDAQUIN_GRAPHICS = BALDAQUIN_ROOT / 'graphics'
BALDAQUIN_ICONS = BALDAQUIN_GRAPHICS / 'icons'
BALDAQUIN_SKINS = BALDAQUIN_GRAPHICS / 'skins'
BALDAQUIN_DOCS = BALDAQUIN_BASE / 'docs'
BALDAQUIN_DOCS_STATIC = BALDAQUIN_DOCS / '_static'
BALDAQUIN_TESTS = BALDAQUIN_BASE / 'test'


def _create_folder(folder_path : Path) -> None:
    """Create a given folder if it does not exist.
    """
    if not folder_path.exists():
        logger.info(f'Creating folder {folder_path}...')
        Path.mkdir(folder_path, parents=True)


# The path to the base folder for the output data defaults to ~/baldaquindata,
# but can be changed via the $BALDAQUIN_DATA environmental variable.
try:
    BALDAQUIN_DATA = Path(os.environ['BALDAQUIN_DATA'])
except KeyError:
    BALDAQUIN_DATA = Path.home() / 'baldaquindata'
_create_folder(BALDAQUIN_DATA)

# On the other hand all the configuration files live in (subdirectories of) ~/.baldaquin
BALDAQUIN_CONFIG = Path.home() / '.baldaquin'
_create_folder(BALDAQUIN_CONFIG)


# Logger setup.
DEFAULT_LOGURU_HANDLER = dict(sink=sys.stderr, colorize=True,
    format=">>> <level>{message}</level>")


def config_logger(file_path : str = None, extra=None):
    """Configure the loguru logger.
    """
    handlers = [DEFAULT_LOGURU_HANDLER]
    if file_path is not None:
        handlers.append(dict(sink=file_path, enqueue=True, serialize=True))
    logger.configure(handlers=handlers, levels=None, extra=extra)


def config_folder_path(project_name : str) -> Path:
    """Return the path to the configuration folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    return BALDAQUIN_CONFIG / project_name


def data_folder_path(project_name : str) -> Path:
    """Return the path to the data folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    return BALDAQUIN_DATA / project_name


def setup_project(project_name : str) -> tuple[Path, Path]:
    """Setup the folder structure for a given project.

    This is essentially creating a folder for the configuration files and
    a folder for the data files, if they do not exist already, and returns
    the path to the two (in this order---first config and then data).
    """
    for folder_path in (config_folder_path(project_name), data_folder_path(project_name)):
        _create_folder(folder_path)
    return config_folder_path, data_folder_path
