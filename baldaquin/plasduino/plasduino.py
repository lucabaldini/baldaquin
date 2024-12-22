# Copyright (C) 22024 the baldaquin team.
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

"""Plasduino common resources.
"""

from baldaquin.serial_ import list_com_ports



# List of supported boards, i.e., only the arduino uno at the moment.
# This comes in the form of a list of (vid, pid) tuples, with the numbers taken
# verbatim from https://github.com/arduino/ArduinoCore-avr/blob/master/boards.txt
# At some point we might want to do a more thorough job of listing all the
# possible (vid, pid) of the actual arduino boards with which plasduino would
# work (I am sure, e.g., that we tested the thing with arduino mega).

_SUPPORTED_BOARDS = (
    (0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x2341, 0x0243), (0x2341, 0x006A), # uno
)



def autodetect_arduino_board() -> str:
    """Autodetect a supported arduino board attached to one the serial ports, and
    return the corresponding device name (e.g., ``/dev/ttyACM0``).

    Note this returns None if no supported arduino board is found, and the the
    first board found in case there are more than one.
    """
    ports = list_com_ports(*_SUPPORTED_BOARDS)
    if len(ports) == 0:
        return None
    if len(ports) > 1:
        logger.warning('More than one arduino board found, picking the first one...')
    return ports[0].device



#if __name__ == '__main__':
#    device = autodetect_arduino_board()
#    print(device)
