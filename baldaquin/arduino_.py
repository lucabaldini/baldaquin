# Copyright (C) 2024 the baldaquin team.
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

"""Arduino common resources.

.. warning::
    We are taking this chance to look around and see what's the best way to interface
    to arduino, and this module might significantly change in the future---at this
    point you should consider all the API as experimental.
"""

from dataclasses import dataclass
import subprocess

import serial.tools.list_ports_common

from baldaquin import logger
from baldaquin import execute_shell_command
from baldaquin.serial_ import list_com_ports


@dataclass
class ArduinoBoard:

    """Small container class representing a specific Arduino board.

    This is not supposed as a mean to replicate all the functionalities of the
    Arduino CLI---on the contrary, we want to include here the bare minimum that
    is necessary in order to do simple things, e.g., auto-recognize Arduino boards
    attached to the serial port and programmatically upload a sketch.

    The ultimate reference for all this information is embedded into the
    (platform-specific) boards.txt file, e.g.,
    https://github.com/arduino/ArduinoCore-avr/blob/master/boards.txt
    Rather than parsing the entire file and come up with a parallel Python structure
    supporting all the boards on the face of the Earth, we decided to manually add
    the necessary data for specific boards only when (and if) we need them, starting
    from the Arduino UNO, being used in plasduino.
    """

    # pylint: disable=too-many-instance-attributes

    board_id: str
    name: str
    vendor: str
    architecture: str
    upload_protocol: str
    upload_speed: int
    build_mcu: str
    identifiers: tuple

    def fqbn(self) -> str:
        """Return the fully qualified board name (FQBN), as defined in
        https://arduino.github.io/arduino-cli/1.1/platform-specification/
        """
        return f'{self.vendor}:{self.architecture}:{self.board_id}'



UNO = ArduinoBoard('uno', 'Arduino UNO', 'arduino', 'avr', 'arduino', 115200, 'atmega328p',
    ((0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x2341, 0x0243), (0x2341, 0x006A)))


_SUPPORTED_BOARDS = (UNO,)


# Build a dictionary {(vid, pid): ArduinoBoard} containing all the supported boards.
# Th is is useful, e.g., when autodetecting arduino boards connected to a serial port.
_BOARD_IDENTIFIER_DICT = {}
for _board in _SUPPORTED_BOARDS:
    for _id in _board.identifiers:
        _BOARD_IDENTIFIER_DICT[_id] = _board


def board_identifiers(*boards: ArduinoBoard) -> tuple:
    """Return all the possible identiers corresponding to a subset of the supported
    arduino boards.

    Arguments
    ---------
    *boards : ArduinoBoard
        The ArduinoBoard object(s) we are interested into.

    Returns
    -------
    tuple
        A tuple of (vid, pid) tuples.
    """
    # If you are tempted to use a sum of lists with start=[], here, keep in mind
    # this is not supported in Python 3.7.
    identiers = ()
    for board in boards:
        identiers += board.identifiers
    return identiers


def identify_arduino_board(vid: int, pid: int) -> ArduinoBoard:
    """Return the ArduinoBoard object corresponding to a given (vid, pid) tuple.

    Arguments
    ---------
    vid : int
        The vendor ID for the given device.

    pid : int
        The prodict ID for the given device.

    Returns
    -------
    ArduinoBoard
        The ArduinoBoard object corresponding to the vid and pid passes as arguments.
    """
    return _BOARD_IDENTIFIER_DICT.get((vid, pid))


def autodetect_arduino_boards(*boards: ArduinoBoard) -> serial.tools.list_ports_common.ListPortInfo:
    """Autodetect all supported arduino boards of one or more specific types
    attached to the COM ports.

    Arguments
    ---------
    *boards : ArduinoBoard
        The ArduinoBoard object(s) we are interested into.

    Returns
    -------
    serial.tools.list_ports_common.ListPortInfo
        See
        https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
        for the object documentation.
    """
    logger.info(f'Autodetecting Arduino boards {[board.name for board in boards]}...')
    ports = list_com_ports(*board_identifiers(*boards))
    for port in ports:
        board = identify_arduino_board(port.vid, port.pid)
        if port is not None:
            logger.info(f'{port.device} -> {board.board_id} ({board.name})')
    return ports


def autodetect_arduino_board(*boards: ArduinoBoard) -> serial.tools.list_ports_common.ListPortInfo:
    """Autodetect the first supported arduino board within a list of board types.

    Note this returns None if no supported arduino board is found, and the
    first board found in case there are more than one.

    Arguments
    ---------
    *boards : ArduinoBoard
        The ArduinoBoard object(s) we are interested into.

    Returns
    -------
    serial.tools.list_ports_common.ListPortInfo
        See
        https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
        for the object documentation.
    """
    ports = autodetect_arduino_boards(*boards)
    if len(ports) == 0:
        return None
    port = ports[0]
    if len(ports) > 1:
        logger.warning(f'More than one arduino board found, picking {port}...')
    return port



class ArduinoProgrammingInterfaceBase:

    """Basic class for concrete interfaces for programming Arduino devices.
    """

    # pylint: disable=too-few-public-methods

    PROGRAM_NAME = None
    PROGRAM_URL = None

    @staticmethod
    def upload(file_path: str, port: str, board: ArduinoBoard,
        **kwargs) -> subprocess.CompletedProcess:
        """Do nothing method, to be reimplented in derived classes.
        """
        raise NotImplementedError

    @classmethod
    def _execute(cls, args) -> subprocess.CompletedProcess:
        """Execute a shell command.

        This is wrapping the basic subprocess functionality, adding some simple
        diagnostics. Note a ``CalledProcessError`` exception is raised if the
        underlying program returns an error code different from zero.

        Arguments
        ---------
        args : any
            All the arguments passed to subprocess.run().

        Returns
        -------
        subprocess.CompletedProcess
            The CompletedProcess object.
        """
        # pylint: disable=raise-missing-from
        try:
            status = execute_shell_command(args)
        except FileNotFoundError:
            logger.error(f'Please make sure {cls.PROGRAM_NAME} is properly installed.')
            if cls.PROGRAM_URL is not None:
                logger.error(f'See {cls.PROGRAM_URL} for more details.')
            raise RuntimeError(f'{cls.PROGRAM_NAME} not found')
        status.check_returncode()
        return status



class ArduinoCli(ArduinoProgrammingInterfaceBase):

    """Poor-man Python interface to the Arduino-CLI.

    The installation instructions for the arduino command-line interface are at
    https://arduino.github.io/arduino-cli/1.1/installation/

    (At least on GNU/Linux) this points to a single file that you can just place
    wherever your $PATH will reach it. For the records: when I run the thing for
    the first time (uploading a sketch to an Arduino UNO) it immediately prompted
    me to install more stuff

    >>> arduino-cli core install arduino:avr

    (which I guess is fine, but it is weighing in as to what we should suggest users
    to install).
    """

    # pylint: disable=line-too-long, too-few-public-methods, arguments-differ

    PROGRAM_NAME = 'arduino-cli'
    PROGRAM_URL = 'https://github.com/arduino/arduino-cli'

    @staticmethod
    def upload(file_path: str, port: str, board: ArduinoBoard,
        verbose: bool = False) -> subprocess.CompletedProcess:
        """Upload a sketch to a board.

        Note this is using avrdude under the hood, so one might wonder why we
        would want to use the Arduino CLI in the first place to upload sketches,
        beside the fact that the FQBN is the only thing that it seems to need to
        make the magic.

        .. code-block:: shell

            Usage:
              arduino-cli upload [flags]

            Examples:
              arduino-cli upload /home/user/Arduino/MySketch -p /dev/ttyACM0 -b arduino:avr:uno
              arduino-cli upload -p 192.168.10.1 -b arduino:avr:uno --upload-field password=abc

            Flags:
                  --board-options strings         List of board options separated by commas. Or can be used multiple times for multiple options.
                  --build-path string             Directory containing binaries to upload.
                  --discovery-timeout duration    Max time to wait for port discovery, e.g.: 30s, 1m (default 1s)
              -b, --fqbn string                   Fully Qualified Board Name, e.g.: arduino:avr:uno
              -h, --help                          help for upload
                  --input-dir string              Directory containing binaries to upload.
              -i, --input-file string             Binary file to upload.
              -p, --port string                   Upload port address, e.g.: COM3 or /dev/ttyACM2
              -m, --profile string                Sketch profile to use
              -P, --programmer string             Programmer to use, e.g: atmel_ice
              -l, --protocol string               Upload port protocol, e.g: serial
              -F, --upload-field key=value        Set a value for a field required to upload.
                  --upload-property stringArray   Override an upload property with a custom value. Can be used multiple times for multiple properties.
              -v, --verbose                       Optional, turns on verbose mode.
              -t, --verify                        Verify uploaded binary after the upload.

            Global Flags:
                  --additional-urls strings   Comma-separated list of additional URLs for the Boards Manager.
                  --config-dir string         Sets the default data directory (Arduino CLI will look for configuration file in this directory).
                  --config-file string        The custom config file (if not specified the default will be used).
                  --json                      Print the output in JSON format.
                  --log                       Print the logs on the standard output.
                  --log-file string           Path to the file where logs will be written.
                  --log-format string         The output format for the logs, can be: text, json (default "text")
                  --log-level string          Messages with this level and above will be logged. Valid levels are: trace, debug, info, warn, error, fatal, panic (default "info")
                  --no-color                  Disable colored output.

        """
        args = [
            ArduinoCli.PROGRAM_NAME, 'upload',
            '--port', port,
            '--fqbn', board.fqbn(),
            '--input-file', file_path
            ]
        if verbose:
            args.append('--verbose')
        return ArduinoCli._execute(args)



class AvrDude(ArduinoProgrammingInterfaceBase):

    """Poor-man Python interface to the avrdude.

    .. code-block:: shell

        Usage: avrdude [options]
            Options:
              -p <partno>                Required. Specify AVR device.
              -b <baudrate>              Override RS-232 baud rate.
              -B <bitclock>              Specify JTAG/STK500v2 bit clock period (us).
              -C <config-file>           Specify location of configuration file.
              -c <programmer>            Specify programmer type.
              -D                         Disable auto erase for flash memory
              -i <delay>                 ISP Clock Delay [in microseconds]
              -P <port>                  Specify connection port.
              -F                         Override invalid signature check.
              -e                         Perform a chip erase.
              -O                         Perform RC oscillator calibration (see AVR053).
              -U <memtype>:r|w|v:<filename>[:format]
                                         Memory operation specification.
                                         Multiple -U options are allowed, each request
                                         is performed in the order specified.
              -n                         Do not write anything to the device.
              -V                         Do not verify.
              -u                         Disable safemode, default when running from a script.
              -s                         Silent safemode operation, will not ask you if
                                         fuses should be changed back.
              -t                         Enter terminal mode.
              -E <exitspec>[,<exitspec>] List programmer exit specifications.
              -x <extended_param>        Pass <extended_param> to programmer.
              -v                         Verbose output. -v -v for more.
              -q                         Quell progress output. -q -q for less.
              -l logfile                 Use logfile rather than stderr for diagnostics.
              -?                         Display this usage.

            avrdude version 6.4, URL: <http://savannah.nongnu.org/projects/avrdude/>

    """

    # pylint: disable=line-too-long, too-few-public-methods, arguments-differ

    PROGRAM_NAME = 'avrdude'
    PROGRAM_URL = 'https://github.com/avrdudes/avrdude'

    @staticmethod
    def upload(file_path: str, port: str, board: ArduinoBoard,
        verbose: bool = False) -> subprocess.CompletedProcess:
        """Upload a sketch to a board.
        """
        args = [
            AvrDude.PROGRAM_NAME, '-V', '-F',
            '-c', board.upload_protocol,
            '-b', f'{board.upload_speed}',
            '-p', board.build_mcu,
            '-P', port,
            '-U', f'flash:w:{file_path}'
            ]
        if verbose:
            args.append('-v')
        AvrDude._execute(args)



# if __name__ == '__main__':
#     file_path = '/data/work/baldaquin/baldaquin/plasduino/sketches/analog_sampling.hex'
#     port = '/dev/ttyACM0'
#     ArduinoCli.upload(file_path, port, UNO)
#     AvrDude.upload(file_path, port, UNO)
