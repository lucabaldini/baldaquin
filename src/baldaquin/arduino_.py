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
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass

from .event import EventHandlerBase
from .logging_ import logger
from .pkt import AbstractPacket
from .serial_ import DeviceId, PortInfo, SerialInterface, list_com_ports

# Initialize the necessary dictionaries to retrieve the boards by device_id or
# designator---these will act as two small databases helping accessing board
# information.
_BOARD_DESIGNATOR_DICT = {}
_DEVICE_ID_DICT = {}


def execute_shell_command(args):
    """Execute a shell command.
    """
    logger.info(f'About to execute "{" ".join(args)}"...')
    return subprocess.run(args, check=True)


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

    The typical entry in the file for a board is something like this:

    .. code-block:: shell

        uno.name=Arduino UNO

        uno.vid.0=0x2341
        uno.pid.0=0x0043
        uno.vid.1=0x2341
        uno.pid.1=0x0001
        uno.vid.2=0x2A03
        uno.pid.2=0x0043
        uno.vid.3=0x2341
        uno.pid.3=0x0243
        uno.vid.4=0x2341
        uno.pid.4=0x006A
        uno.upload_port.0.vid=0x2341
        uno.upload_port.0.pid=0x0043
        uno.upload_port.1.vid=0x2341
        uno.upload_port.1.pid=0x0001
        uno.upload_port.2.vid=0x2A03
        uno.upload_port.2.pid=0x0043
        uno.upload_port.3.vid=0x2341
        uno.upload_port.3.pid=0x0243
        uno.upload_port.4.vid=0x2341
        uno.upload_port.4.pid=0x006A
        uno.upload_port.5.board=uno

        uno.upload.tool=avrdude
        uno.upload.tool.default=avrdude
        uno.upload.tool.network=arduino_ota
        uno.upload.protocol=arduino
        uno.upload.maximum_size=32256
        uno.upload.maximum_data_size=2048
        uno.upload.speed=115200

        uno.bootloader.tool=avrdude
        uno.bootloader.tool.default=avrdude
        uno.bootloader.low_fuses=0xFF
        uno.bootloader.high_fuses=0xDE
        uno.bootloader.extended_fuses=0xFD
        uno.bootloader.unlock_bits=0x3F
        uno.bootloader.lock_bits=0x0F
        uno.bootloader.file=optiboot/optiboot_atmega328.hex

        uno.build.mcu=atmega328p
        uno.build.f_cpu=16000000L
        uno.build.board=AVR_UNO
        uno.build.core=arduino
        uno.build.variant=standard

    Note that we refer to the qualifier for the board ("uno" in this case) as
    the board `designator`, and we parse the bare minimum of the information
    from the file.

    """

    # pylint: disable=too-many-instance-attributes

    designator: str
    name: str
    vendor: str
    architecture: str
    upload_protocol: str
    upload_speed: int
    build_mcu: str
    device_ids: tuple[DeviceId]

    def __post_init__(self):
        """Post-initialization: turn the vid, pid tuples into DeviceId objects.
        """
        self.device_ids = tuple(DeviceId(*tup) for tup in self.device_ids)

    def fqbn(self) -> str:
        """Return the fully qualified board name (FQBN), as defined in
        https://arduino.github.io/arduino-cli/1.1/platform-specification/
        """
        return f"{self.vendor}:{self.architecture}:{self.designator}"

    @staticmethod
    def concatenate_device_ids(*boards: ArduinoBoard) -> tuple[DeviceId]:
        """Return a tuple with all the possible DeviceId objects corresponding to a
        subset of the supported arduino boards.

        Arguments
        ---------
        *boards : ArduinoBoard
            The ArduinoBoard object(s) we are interested into.

        Returns
        -------
        tuple
            A tuple of DeviceId objects.
        """
        # If you are tempted to use a sum of lists with start=[], here, keep in mind
        # this is not supported in Python 3.7.
        device_ids = ()
        for board in boards:
            device_ids += board.device_ids
        return device_ids

    @staticmethod
    def by_device_id(device_id: DeviceId) -> ArduinoBoard:
        """Return the ArduinoBoard object corresponding to a given DeviceId.

        Note this only involves a dictionary lookup, and nothing is created on
        the spot.

        Arguments
        ---------
        vid : int
            The vendor ID for the given device.

        pid : int
            The prodict ID for the given device.

        Returns
        -------
        ArduinoBoard
            The ArduinoBoard object corresponding to the DeviceId.
        """
        try:
            return _DEVICE_ID_DICT[device_id]
        except KeyError as exception:
            raise RuntimeError(f"Unsupported device ID {device_id}") from exception

    @staticmethod
    def by_designator(designator: str) -> ArduinoBoard:
        """Return the ArduinoBoard object corresponding to a given (vid, pid) tuple.

        Note this only involves a dictionary lookup, and nothing is created on
        the spot.

        Arguments
        ---------
        designator : str
            The board designator (e.g., "uno").

        Returns
        -------
        ArduinoBoard
            The ArduinoBoard object corresponding to the designator.
        """
        try:
            return _BOARD_DESIGNATOR_DICT[designator]
        except KeyError as exception:
            raise RuntimeError(f"Unsupported designator {designator}") from exception


# --------------------------------------------------------------------------------------------------
# Define the supported boards.
UNO = ArduinoBoard("uno", "Arduino UNO", "arduino", "avr", "arduino", 115200, "atmega328p",
                   ((0x2341, 0x0043),
                    (0x2341, 0x0001),
                    (0x2A03, 0x0043),
                    (0x2341, 0x0243),
                    (0x2341, 0x006A)))


_SUPPORTED_BOARDS = (UNO,)
# --------------------------------------------------------------------------------------------------


# And now loop over the supported boards to fill the information in the dictionaries.
for _board in _SUPPORTED_BOARDS:
    _BOARD_DESIGNATOR_DICT[_board.designator] = _board
    for _id in _board.device_ids:
        _DEVICE_ID_DICT[_id] = _board


def autodetect_arduino_boards(*boards: ArduinoBoard) -> list[PortInfo]:
    """Autodetect all supported arduino boards of one or more specific types
    attached to the COM ports.

    Arguments
    ---------
    *boards : ArduinoBoard
        The ArduinoBoard object(s) we are interested into.

    Returns
    -------
    list of PortInfo objects
        The list of PortInfo object with relevant boards attached to them.
    """
    # If we are passing no boards, we are interested in all the supported ones.
    if len(boards) == 0:
        boards = _SUPPORTED_BOARDS
    logger.info(f"Autodetecting Arduino boards {[board.name for board in boards]}...")
    ports = list_com_ports(*ArduinoBoard.concatenate_device_ids(*boards))
    for port in ports:
        board = ArduinoBoard.by_device_id(port.device_id)
        if port is not None:
            logger.debug(f"{port.name} -> {board.designator} ({board.name})")
    return ports


def autodetect_arduino_board(*boards: ArduinoBoard) -> PortInfo:
    """Autodetect the first supported arduino board within a list of board types.

    Note this returns None if no supported arduino board is found, and the
    first board found in case there are more than one.

    Arguments
    ---------
    *boards : ArduinoBoard
        The ArduinoBoard object(s) we are interested into.

    Returns
    -------
    PortInfo
        The PortInfo object our target board is attached to.
    """
    ports = autodetect_arduino_boards(*boards)
    if len(ports) == 0:
        return None
    port = ports[0]
    if len(ports) > 1:
        logger.warning(f"More than one arduino board found, picking {port}...")
    return port


class ArduinoProgrammingInterfaceBase:

    """Basic class for concrete interfaces for programming Arduino devices.
    """

    # pylint: disable=too-few-public-methods

    PROGRAM_NAME = None
    PROGRAM_URL = None
    SKETCH_EXTENSION = ".ino"
    ARTIFACT_EXTENSION = ".hex"

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
            logger.error(f"Please make sure {cls.PROGRAM_NAME} is properly installed.")
            if cls.PROGRAM_URL is not None:
                logger.error(f"See {cls.PROGRAM_URL} for more details.")
            raise RuntimeError(f"{cls.PROGRAM_NAME} not found") # noqa B904
        return status

    @staticmethod
    def folder_path(sketch_path: str) -> str:
        """Return the folder path (without the trailing directory separator) for
        a given file path pointing to a sketch source file or to the folder containing it.

        The basic arduino convention is that the sketch source file should be named
        after the sketch name, with the .ino extension, and the sketch should be
        in a directory with the same name (without extension). For example,
        ``sketches/test/test.ino``, ``sketches/test/`` and ``sketches/test``
        should all be resolved to ``sketches/test``.

        Note that this function operates purely on strings, and no check is performed
        that the path passed as an argument actually exists.

        Arguments
        ---------
        sketch_path : str
            The path to the sketch source file or to the folder containing it
            (either with or without the trailing folder separator).

        Returns
        -------
        str
            The path to the folder containing the sketch.
        """
        sketch_path = str(sketch_path)
        if sketch_path.endswith(ArduinoProgrammingInterfaceBase.SKETCH_EXTENSION):
            folder_path = os.path.dirname(sketch_path)
        else:
            # Note we need to trim out the trailing directory separator, otherwise
            # the basename will be empty.
            folder_path = sketch_path.rstrip(os.path.sep)
        return folder_path

    @staticmethod
    def project_base_name(sketch_path: str) -> str:
        """Return the base project name for a given file path pointing to a sketch
        source file or to the folder containing it.

        Note that this function operates purely on strings, and no check is performed
        that the path passed as an argument actually exists.

        Arguments
        ---------
        sketch_path : str
            The path to the sketch source file or to the folder containing it
            (either with or without the trailing folder separator).

        Returns
        -------
        str
            The base name of the sketch project.
        """
        return os.path.basename(ArduinoProgrammingInterfaceBase.folder_path(sketch_path))

    @staticmethod
    def project_name(sketch_path: str, board_designator: str) -> str:
        """Return the actual project name for a compiled sketch, given the path
        to the sketch source and the target board designator.
        """
        base_name = ArduinoProgrammingInterfaceBase.project_base_name(sketch_path)
        return f"{base_name}_{board_designator}"

    @staticmethod
    def artifact_name(sketch_name: str, board_designator: str) -> str:
        """Return the name of the artifact for a given sketch and board designator.
        """
        return f"{sketch_name}_{board_designator}"\
               f"{ArduinoProgrammingInterfaceBase.ARTIFACT_EXTENSION}"


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

    PROGRAM_NAME = "arduino-cli"
    PROGRAM_URL = "https://github.com/arduino/arduino-cli"

    @staticmethod
    def upload(file_path: str, port: str, board: ArduinoBoard,
               verbose: bool = False) -> subprocess.CompletedProcess:
        """Upload a sketch to a board.

        Note this is using avrdude under the hood.

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

        """  # noqa F811
        args = [
            ArduinoCli.PROGRAM_NAME, "upload",
            "--port", port,
            "--fqbn", board.fqbn(),
            # Note we have to cast to string in case file_path is a Path, as
            # subprocess is adamant in requiring a string.
            "--input-file", str(file_path)
            ]
        if verbose:
            args.append("--verbose")
        return ArduinoCli._execute(args)

    @staticmethod
    def compile(sketch_path: str, output_dir: str, board: ArduinoBoard,
                verbose: bool = False, copy_artifacts: bool = True) -> subprocess.CompletedProcess:
        """Compile a sketch.

        Note the board designator is appended to the name of the output artifacts,
        so that we can keep track of the different versions of the same sketch compiled
        for different boards.

        By default the compilation artifacts are copied to the original sketch folder.

        Arguments
        ---------
        sketch_path : str
            The path to the sketch source file or to the folder containing it.

        output_dir : str
            Path to the folder where the compilation artifacts should be placed.

        board : ArduinoBoard
            The board to compile the sketch for.

        verbose : bool
            If True, the program will run in verbose mode.

        copy_artifacts : bool
            If True, the compilation artifacts will be copied to the original sketch folder.

        Returns
        -------
        subprocess.CompletedProcess
            The CompletedProcess object.

        .. code-block:: shell

            Usage:
              arduino-cli compile [flags]

            Examples:
              arduino-cli compile -b arduino:avr:uno /home/user/Arduino/MySketch
              arduino-cli compile -b arduino:avr:uno --build-property "build.extra_flags=\"-DMY_DEFINE=\"hello world\"\"" /home/user/Arduino/MySketch
              arduino-cli compile -b arduino:avr:uno --build-property "build.extra_flags=-DPIN=2 \"-DMY_DEFINE=\"hello world\"\"" /home/user/Arduino/MySketch
              arduino-cli compile -b arduino:avr:uno --build-property build.extra_flags=-DPIN=2 --build-property "compiler.cpp.extra_flags=\"-DSSID=\"hello world\"\"" /home/user/Arduino/MySketch


            Flags:
                  --board-options strings                 List of board options separated by commas. Or can be used multiple times for multiple options.
                  --build-path string                     Path where to save compiled files. If omitted, a directory will be created in the default temporary path of your OS.
                  --build-property stringArray            Override a build property with a custom value. Can be used multiple times for multiple properties.
                  --clean                                 Optional, cleanup the build folder and do not use any cached build.
                  --discovery-timeout duration            Max time to wait for port discovery, e.g.: 30s, 1m (default 1s)
                  --dump-profile                          Create and print a profile configuration from the build.
                  --encrypt-key string                    The name of the custom encryption key to use to encrypt a binary during the compile process. Used only by the platforms that support it.
              -e, --export-binaries                       If set built binaries will be exported to the sketch folder.
              -b, --fqbn string                           Fully Qualified Board Name, e.g.: arduino:avr:uno
              -h, --help                                  help for compile
              -j, --jobs int32                            Max number of parallel compiles. If set to 0 the number of available CPUs cores will be used.
                  --keys-keychain string                  The path of the dir to search for the custom keys to sign and encrypt a binary. Used only by the platforms that support it.
                  --libraries strings                     Path to a collection of libraries. Can be used multiple times or entries can be comma separated.
                  --library strings                       Path to a single library’s root folder. Can be used multiple times or entries can be comma separated.
                  --only-compilation-database             Just produce the compilation database, without actually compiling. All build commands are skipped except pre* hooks.
                  --optimize-for-debug                    Optional, optimize compile output for debugging, rather than for release.
                  --output-dir string                     Save build artifacts in this directory.
              -p, --port string                           Upload port address, e.g.: COM3 or /dev/ttyACM2
                  --preprocess                            Print preprocessed code to stdout instead of compiling.
              -m, --profile string                        Sketch profile to use
              -P, --programmer string                     Programmer to use, e.g: atmel_ice
              -l, --protocol string                       Upload port protocol, e.g: serial
                  --quiet                                 Optional, suppresses almost every output.
                  --show-properties string[="expanded"]   Show build properties. The properties are expanded, use "--show-properties=unexpanded" if you want them exactly as they are defined. (default "disabled")
                  --sign-key string                       The name of the custom signing key to use to sign a binary during the compile process. Used only by the platforms that support it.
              -u, --upload                                Upload the binary after the compilation.
              -v, --verbose                               Optional, turns on verbose mode.
              -t, --verify                                Verify uploaded binary after the upload.
                  --warnings string                       Optional, can be: none, default, more, all. Used to tell gcc which warning level to use (-W flag). (default "none")

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

        """ # noqa F811
        # Cache the project name for the sketch.
        project_name = ArduinoCli.project_name(sketch_path, board.designator)
        # Path to the output (compiled) file.
        file_name = f"{project_name}.hex"

        # Assemble the arguments and execute the compilation command.
        args = [
            ArduinoCli.PROGRAM_NAME, "compile",
            "--output-dir", str(output_dir),
            "--fqbn", board.fqbn(),
            "--build-property", f"build.project_name={project_name}",
            str(sketch_path)
            ]
        if verbose:
            args.append("--verbose")
        status = ArduinoCli._execute(args)

        # If necessary, copy the compilation artifacts to the source sketch folder.
        if copy_artifacts:
            src = os.path.join(output_dir, file_name)
            dest = os.path.join(ArduinoCli.folder_path(sketch_path), file_name)
            logger.info(f"Copying {src} to {dest}...")
            shutil.copyfile(src, dest)

        return status


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

    PROGRAM_NAME = "avrdude"
    PROGRAM_URL = "https://github.com/avrdudes/avrdude"

    @staticmethod
    def upload(file_path: str, port: str, board: ArduinoBoard,
               verbose: bool = False) -> subprocess.CompletedProcess:
        """Upload a sketch to a board.
        """
        args = [
            AvrDude.PROGRAM_NAME, "-V", "-F",
            "-c", board.upload_protocol,
            "-b", f"{board.upload_speed}",
            "-p", board.build_mcu,
            "-P", port,
            "-U", f"flash:w:{file_path}"
            ]
        if verbose:
            args.append("-v")
        return AvrDude._execute(args)


def upload_sketch(file_path: str, board_designator: str,
                  port_name: str = None, verbose: bool = False) -> subprocess.CompletedProcess:
    """High-level interface to upload a compiled sketch to an arduino board.

    Arguments
    ---------
    file_path : str
        The path to the binary file containing the sketch compiled for the given
        board.

    board_designator : str
        The board designator (e.g., "uno").

    port_name : str, optional
        The port name the board is attached to (e.g., "/dev/ttyACM0"). If this is
        None, we use the autodetection features implemented in the module.

    verbose : bool
        If True, the program will run in verbose mode.
    """
    if not os.path.exists(file_path):
        raise RuntimeError(f"Could not find file {file_path}")
    board = ArduinoBoard.by_designator(board_designator)
    if port_name is None:
        port = autodetect_arduino_board(board)
        if port is None:
            raise RuntimeError(f"Could not autodetect port with {board.name}")
        port_name = port.name
    logger.info(f"Uploading sketch {file_path} for {board} to port {port_name}...")
    return ArduinoCli.upload(file_path, port_name, board, verbose)


def compile_sketch(file_path: str, board_designator: str, output_dir: str,
                   verbose: bool = False) -> subprocess.CompletedProcess:
    """High-level interface to compile a sketch for a given arduino board.

    Arguments
    ---------
    file_path : str
        The path to the binary file containing the sketch compiled for the given
        board. Note that, in virtue of some interesting decision by the Arduino
        team, it appears that the main source file for the sketch should be embedded
        in a folder with the same name (without extension)---I guess that vaguely
        makes sense for sketches with multiple files. The directory name is also
        gladly accepted for the compilation.

    board_designator : str
        The board designator (e.g., "uno").

    output_dir : str
        Path to the folder where the compilation artifacts should be placed.

    verbose : bool
        If True, the program will run in verbose mode.
    """
    if not os.path.exists(file_path):
        raise RuntimeError(f"Could not find file {file_path}")
    board = ArduinoBoard.by_designator(board_designator)
    logger.info(f"Compiling sketch {file_path} for {board}...")
    return ArduinoCli.compile(file_path, output_dir, board, verbose)


class ArduinoSerialInterface(SerialInterface):

    """Specialized serial interface to interact with arduino boards.
    """

    # pylint: disable=too-many-ancestors

    def handshake(self, sketch_name: str, sketch_version: int, sketch_folder_path: str,
                  timeout: float = 5.) -> None:
        """Simple handshake routine to check that the proper sketch is uploaded
        on the arduino board attached to the serial port, and upload the sketch
        if that is not the case.
        """
        logger.info("Performing handshake with the Arduino board...")
        # Temporarily set a finite timeout to handle the case where there is not
        # sensible sketch pre-loaded on the board, and we have to start from scratch.
        # (And we need to cache the previous timeout value in order to restore it later).
        previous_timeout = self.timeout
        self.set_timeout(timeout)
        # Read the sketch name and version from the board.
        try:
            name, version = self.read_text_line().unpack(str, int)
            logger.info(f"Sketch {name} version {version} loaded onboard...")
        except RuntimeError as exception:
            logger.warning("Could not determine the sketch loaded onboard.")
            logger.debug(exception)
            name, version = None, None
        # Now put back the actual target timeout.
        self.set_timeout(previous_timeout)
        # If the sketch uploaded onboard is the one we expect, we're good to go.
        if (name, version) == (sketch_name, sketch_version):
            logger.info("Sketch is up to date, nothing to do!")
            return
        # Otherwise, we need to upload the proper sketch and, before that,
        # retrieve the specific board we are talking to---this information is
        # available in the PortInfo object attached to the serial interface
        # at connection time.
        logger.info(f"Triggering upload of sketch {sketch_name} version {sketch_version}...")
        board = ArduinoBoard.by_device_id(self.port_info.device_id)
        file_name = ArduinoCli.artifact_name(sketch_name, board.designator)
        file_path = os.path.join(sketch_folder_path, sketch_name, file_name)
        # Upload the proper sketch and make sure we are in business.
        upload_sketch(file_path, board.designator, self.port)
        name, version = self.read_text_line().unpack(str, int)
        if (name, version) != (sketch_name, sketch_version):
            raise RuntimeError(f"Could not upload sketch {name} version {version}")


class ArduinoEventHandler(EventHandlerBase):

    """Base class for all the Arduino event handlers.
    """

    SERIAL_INTERFACE_CLASS = ArduinoSerialInterface

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        self.serial_interface = self.SERIAL_INTERFACE_CLASS()

    def read_packet(self) -> AbstractPacket:
        """Overloaded (still abstract) method.
        """
        raise NotImplementedError

    def open_serial_interface(self, timeout: float = None) -> None:
        """Open the serial interface.
        """
        port_info = autodetect_arduino_board(*_SUPPORTED_BOARDS)
        if port_info is None:
            raise RuntimeError("Could not find a suitable arduino board connected.")
        self.serial_interface.connect(port_info, timeout=timeout)
        self.serial_interface.pulse_dtr()

    def close_serial_interface(self) -> None:
        """Close the serial interface.
        """
        self.serial_interface.disconnect()
