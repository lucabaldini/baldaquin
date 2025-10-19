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

"""baldaquin command-line interface.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys

from baldaquin import __version__, arduino_, serial_
from baldaquin.env import BALDAQUIN_DATA, BALDAQUIN_SOURCE
from baldaquin.logging_ import logger

# List of defaults projects shipped with the package.
_DEFAULT_PROJECTS = ("plasduino", "silly")


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


class _Formatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):

    """Do nothing class combining our favorite formatting for the
    command-line options, i.e., the newlines in the descriptions are
    preserved and, at the same time, the argument defaults are printed
    out when the --help options is passed.

    The inspiration for this is coming from one of the comments in
    https://stackoverflow.com/questions/3853722
    """


class MainArgumentParser(argparse.ArgumentParser):

    """Application-wide argument parser.
    """

    _DESCRIPTION = None
    _EPILOG = None
    _FORMATTER_CLASS = _Formatter

    def __init__(self) -> None:
        """Overloaded method.
        """
        super().__init__(description=self._DESCRIPTION, epilog=self._EPILOG,
                         formatter_class=self._FORMATTER_CLASS)
        subparsers = self.add_subparsers(required=True, help="sub-command help")
        # See https://stackoverflow.com/questions/8757338/
        subparsers._parser_class = argparse.ArgumentParser

        # Start a given application.
        start_app = subparsers.add_parser("start-app",
            help="start a baldaquin application",
            formatter_class=self._FORMATTER_CLASS)
        start_app.add_argument("app_name", choices=self.list_apps())
        start_app.set_defaults(func=self.start_app)

        # Simply list the COM ports.
        list_com_ports = subparsers.add_parser("list-com-ports",
            help="list the available COM ports",
            formatter_class=self._FORMATTER_CLASS)
        list_com_ports.set_defaults(func=serial_.list_com_ports)

        # Arduino autodetect.
        arduino_autodetect = subparsers.add_parser("arduino-autodetect",
            help="autodetect arduino boards attached to the COM ports",
            formatter_class=self._FORMATTER_CLASS)
        arduino_autodetect.set_defaults(func=arduino_.autodetect_arduino_boards)

        # Arduino upload.
        arduino_compile = subparsers.add_parser("arduino-compile",
            help="compile a sketch for a given arduino board",
            formatter_class=self._FORMATTER_CLASS)
        arduino_compile.add_argument("file_path",
            help="the path to the sketch source file")
        arduino_compile.add_argument("--output_dir", default=BALDAQUIN_DATA)
        arduino_compile.add_argument("--board_designator", default="uno")
        arduino_compile.set_defaults(func=arduino_.compile_sketch)

        # Arduino upload.
        arduino_upload = subparsers.add_parser("arduino-upload",
            help="upload a sketch to an arduino board",
            formatter_class=self._FORMATTER_CLASS)
        arduino_upload.add_argument("file_path",
            help="the path to the compiled sketch file")
        arduino_upload.add_argument("--board-designator", default="uno")
        arduino_upload.set_defaults(func=arduino_.upload_sketch)

    @staticmethod
    def list_apps() -> list[str]:
        """List all the available applications.

        This is looping over all the registered project folders and searching
        for Python modules. Note that ``pathlib.Path.iterdir()`` returns a list
        in no particular order, and we do sort the list in place for convenience.
        """
        apps = []
        for project in _DEFAULT_PROJECTS:
            folder_path = BALDAQUIN_SOURCE / project / "apps"
            apps += [_path.stem for _path in folder_path.iterdir() if _path.suffix == ".py"]
        apps.sort()
        return apps

    @staticmethod
    def start_app(app_name: str) -> None:
        """Start a given application.

        Arguments
        ---------
        app_name : str
            The application name.
        """
        logger.info("Starting application...")
        # Loop over the project folders and search for a Python module matching the
        # target application name.
        for project in _DEFAULT_PROJECTS:
            folder_path = BALDAQUIN_SOURCE / project / "apps"
            file_path = folder_path / f"{app_name}.py"
            if file_path.exists():
                logger.debug(f"Adding {file_path} to sys.path...")
                sys.path.append(str(folder_path))
                break
        # At this point we do want to import the module without generating the
        # bytecode---we cannot assume the thing is in a folder with write priviledges.
        sys.dont_write_bytecode = True
        module = importlib.import_module(app_name)
        sys.dont_write_bytecode = False
        # And, finally, we call the application entry point.
        module.main()

    def run_command(self) -> None:
        """Run the actual command tied to the specific options.
        """
        kwargs = vars(self.parse_args())
        command = kwargs.pop("func")
        command(**kwargs)


def main() -> None:
    """Main entry point.
    """
    start_message()
    MainArgumentParser().run_command()


if __name__ == "__main__":
    main()
