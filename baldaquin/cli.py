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

import argparse

from baldaquin import BALDAQUIN_DATA
from baldaquin import arduino_
from baldaquin import serial_


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
        subparsers = self.add_subparsers(required=True, help='sub-command help')
        # See https://stackoverflow.com/questions/8757338/
        subparsers._parser_class = argparse.ArgumentParser

        # Simply list the COM ports.
        list_com_ports = subparsers.add_parser('list-com-ports',
            help='list the available COM ports',  # noqa: E128
            formatter_class=self._FORMATTER_CLASS)  # noqa: E128
        list_com_ports.set_defaults(func=serial_.list_com_ports)

        # Arduino autodetect.
        arduino_autodetect = subparsers.add_parser('arduino-autodetect',
            help='autodetect arduino boards attached to the COM ports',  # noqa: E128
            formatter_class=self._FORMATTER_CLASS)  # noqa: E128
        arduino_autodetect.set_defaults(func=arduino_.autodetect_arduino_boards)

        # Arduino upload.
        arduino_compile = subparsers.add_parser('arduino-compile',
            help='compile a sketch for a given arduino board',  # noqa: E128
            formatter_class=self._FORMATTER_CLASS)  # noqa: E128
        arduino_compile.add_argument('file_path',
            help='the path to the sketch source file')  # noqa: E128
        arduino_compile.add_argument('--output_dir', default=BALDAQUIN_DATA)
        arduino_compile.add_argument('--board-designator', default='uno')
        arduino_compile.set_defaults(func=arduino_.compile_sketch)

        # Arduino upload.
        arduino_upload = subparsers.add_parser('arduino-upload',
            help='upload a sketch to an arduino board',  # noqa: E128
            formatter_class=self._FORMATTER_CLASS)  # noqa: E128
        arduino_upload.add_argument('file_path',
            help='the path to the compiled sketch file')  # noqa: E128
        arduino_upload.add_argument('--board', default=arduino_.UNO)
        arduino_upload.set_defaults(func=arduino_.upload_sketch)

    def run_command(self) -> None:
        """Run the actual command tied to the specific options.
        """
        kwargs = vars(self.parse_args())
        command = kwargs.pop('func')
        command(**kwargs)


def main() -> None:
    """Main entry point.
    """
    MainArgumentParser().run_command()


if __name__ == '__main__':
    main()
