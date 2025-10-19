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

"""System-wide facilities.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

from loguru import logger

from baldaquin._version import __version__ as __base_version__


def _git_suffix() -> str:
    """If we are in a git repo, we want to add the necessary information to the
    version string.

    This will return something along the lines of ``+gf0f18e6.dirty``.
    """
    # pylint: disable=broad-except
    kwargs = dict(cwd=pathlib.Path(__file__).parent, stderr=subprocess.DEVNULL)
    try:
        # Retrieve the git short sha to be appended to the base version string.
        args = ["git", "rev-parse", "--short", "HEAD"]
        sha = subprocess.check_output(args, **kwargs).decode().strip()
        suffix = f"+g{sha}"
        # If we have uncommitted changes, append a `.dirty` to the version suffix.
        args = ["git", "diff", "--quiet"]
        if subprocess.call(args, stdout=subprocess.DEVNULL, **kwargs) != 0:
            suffix = f"{suffix}.dirty"
        return suffix
    except Exception:
        return ""


__version__ = f"{__base_version__}{_git_suffix()}"



def start_message() -> None:
    """Print the start message.
    """
    msg = f"""
    This is baldaquin version {__version__}.

    Copyright (C) 2022--2025, the baldaquin team.

    baldaquin comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it under certain
    conditions. See the LICENSE file for details.

    Visit https://github.com/lucabaldini/baldaquin for more information.
    """
    print(msg)


#start_message()


def reset_logger(level: str = 'DEBUG') -> int:
    """Minimal configuration facility for the loguru logger.

    A few remarks about the loguru internals. In order to keep the API clean, the
    author of the library made the deliberate decision not to allow to change handlers,
    so that the preferred way to change the logger configuration is to remove all the
    existing handlers and start from scratch---this is exactly what we are doing here.

    Also note that whenever you add a new handler, you get back an ID that can be used
    to remove the handler later on. The default handler (which we get rid of at the
    first call to this function) is guaranteed to have ID 0.

    Arguments
    ---------
    level : str
        The minimum logging level to be used by the logger. Defaults to 'DEBUG'.
        Other possible values are 'INFO', 'WARNING', 'ERROR', and 'CRITICAL'.

    Returns
    -------
    int
        The ID of the handler that was added.
    """
    # Remove all existing handlers.
    logger.remove()
    # Create a plain, terminal-based logger.
    fmt = '>>> <level>[{level}] {message}</level>'
    return logger.add(sys.stderr, level=level, colorize=True, format=fmt)


def add_log_file(file_path: str, level: str = 'DEBUG') -> int:
    """Add a new file-based handler to the logger.

    Arguments
    ---------
    file_path : str
        The path to the file where the log messages should be written.

    level : str
        The minimum logging level to be used by the logger. Defaults to 'DEBUG'.
    """
    logger.info(f'Directing logger output to {file_path} (level={level})...')
    return logger.add(file_path, level=level)


reset_logger()


# Basic package structure.
BALDAQUIN_ROOT = pathlib.Path(__file__).parent
BALDAQUIN_BASE = BALDAQUIN_ROOT.parent.parent
BALDAQUIN_GRAPHICS = BALDAQUIN_ROOT / 'graphics'
BALDAQUIN_ICONS = BALDAQUIN_GRAPHICS / 'icons'
BALDAQUIN_SKINS = BALDAQUIN_GRAPHICS / 'skins'
BALDAQUIN_DOCS = BALDAQUIN_BASE / 'docs'
BALDAQUIN_DOCS_STATIC = BALDAQUIN_DOCS / '_static'


# Version information.
BALDAQUIN_VERSION_FILE_PATH = BALDAQUIN_ROOT / '_version.py'


# pyproject.toml file.
BALDAQUIN_TOML_FILE_PATH = BALDAQUIN_BASE / 'pyproject.toml'


# Release notes file.
BALDAQUIN_RELEASE_NOTES_PATH = BALDAQUIN_DOCS / 'release_notes.rst'


# Default character encoding.
DEFAULT_CHARACTER_ENCODING = 'utf-8'


def execute_shell_command(args):
    """Execute a shell command.
    """
    logger.info(f'About to execute "{" ".join(args)}"...')
    return subprocess.run(args, check=True)


def _create_folder(folder_path: pathlib.Path) -> None:
    """Create a given folder if it does not exist.

    This is a small utility function to ensure that the relevant directories
    exist when needed at runtime.

    Arguments
    ---------
    folder_path : Path instance
        The path to the target folder.
    """
    if not folder_path.exists():
        logger.info(f'Creating folder {folder_path}...')
        pathlib.Path.mkdir(folder_path, parents=True)


# The path to the base folder for the output data defaults to ~/baldaquindata,
# but can be changed via the $BALDAQUIN_DATA environmental variable.
try:
    BALDAQUIN_DATA = pathlib.Path(os.environ['BALDAQUIN_DATA'])
except KeyError:
    BALDAQUIN_DATA = pathlib.Path.home() / 'baldaquindata'
_create_folder(BALDAQUIN_DATA)


# We're doing a similar thing for our scratch space.
try:
    BALDAQUIN_SCRATCH = pathlib.Path(os.environ['BALDAQUIN_SCRATCH'])
except KeyError:
    BALDAQUIN_SCRATCH = BALDAQUIN_DATA / 'scratch'
_create_folder(BALDAQUIN_SCRATCH)


# On the other hand all the configuration files live in (subdirectories of) ~/.baldaquin
BALDAQUIN_CONFIG = pathlib.Path.home() / '.baldaquin'
_create_folder(BALDAQUIN_CONFIG)


def config_folder_path(project_name: str) -> pathlib.Path:
    """Return the path to the configuration folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    return BALDAQUIN_CONFIG / project_name


def data_folder_path(project_name: str) -> pathlib.Path:
    """Return the path to the data folder for a given project.

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    return BALDAQUIN_DATA / project_name


def setup_project(project_name: str) -> tuple[pathlib.Path, pathlib.Path]:
    """Setup the folder structure for a given project.

    This is essentially creating a folder for the configuration files and
    a folder for the data files, if they do not exist already, and returns
    the path to the two (in this order---first config and then data).

    Arguments
    ---------
    project_name : str
        The name of the project.
    """
    config_folder = config_folder_path(project_name)
    app_config_folder = config_folder / 'apps'
    data_folder = data_folder_path(project_name)
    folder_list = (config_folder, app_config_folder, data_folder)
    for folder_path in folder_list:
        _create_folder(folder_path)
    return folder_list
