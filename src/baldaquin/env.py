# Copyright (C) 2025 the baldaquin team.
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


"""Basic package environment settings.
"""

import os
import pathlib
from typing import Tuple

from .logging_ import logger
from .typing_ import PathLike


def resolve(path: PathLike) -> pathlib.Path:
    """Resolve a given path, in the form of a pathlib.Path instance or a string.

    Path.resolve() returns an absolute, normalized path with all symbolic links
    resolved (if possible).

    Arguments
    ---------
    folder_path : Path instance
        The path to be resolved.

    Returns
    -------
    Path
        The resolved path.
    """
    return pathlib.Path(path).resolve()


def _mkdir(folder_path: PathLike) -> None:
    """Create a given folder if it does not exist.

    This is a small utility function to ensure that the relevant directories
    exist when needed at runtime.

    Arguments
    ---------
    folder_path : Path instance
        The path to the target folder.
    """
    folder_path = resolve(folder_path)
    if not folder_path.exists():
        logger.info(f"Creating folder {folder_path}...")
        pathlib.Path.mkdir(folder_path, parents=True)


# Basic package structure. Note we are using the typical src layout for the package.
BALDAQUIN_SOURCE = pathlib.Path(__file__).parent
BALDAQUIN_ROOT = BALDAQUIN_SOURCE.parent.parent
BALDAQUIN_GRAPHICS = BALDAQUIN_SOURCE / "graphics"
BALDAQUIN_ICONS = BALDAQUIN_GRAPHICS / "icons"
BALDAQUIN_SKINS = BALDAQUIN_GRAPHICS / "skins"

# System-wide character encoding.
BALDAQUIN_ENCODING = os.getenv("BALDAQUIN_ENCODING", "utf-8")

# User folders for data, scratch files, and configuration files. Note these can
# be overridden via environment variables.
_HOME = pathlib.Path.home()
BALDAQUIN_DATA = resolve(os.getenv("BALDAQUIN_DATA", _HOME / "baldaquindata"))
_mkdir(BALDAQUIN_DATA)

BALDAQUIN_SCRATCH = resolve(os.getenv("BALDAQUIN_SCRATCH", _HOME / ".baldaquinscratch"))
_mkdir(BALDAQUIN_SCRATCH)

BALDAQUIN_CONFIG = resolve(os.getenv("BALDAQUIN_CONFIG", _HOME / ".baldaquin"))
_mkdir(BALDAQUIN_CONFIG)


def config_folder_path(project_name: str) -> pathlib.Path:
    """Return the path to the configuration folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.

    Returns
    -------
    Path
        The path to the configuration folder.
    """
    return BALDAQUIN_CONFIG / project_name


def data_folder_path(project_name: str) -> pathlib.Path:
    """Return the path to the data folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.

    Returns
    -------
    Path
        The path to the data folder.
    """
    return BALDAQUIN_DATA / project_name


def setup_project(project_name: str) -> Tuple[pathlib.Path, pathlib.Path]:
    """Setup the folder structure for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    config_folder = config_folder_path(project_name)
    app_config_folder = config_folder / "apps"
    data_folder = data_folder_path(project_name)
    folder_list = (config_folder, app_config_folder, data_folder)
    for folder_path in folder_list:
        _mkdir(folder_path)
    return folder_list
