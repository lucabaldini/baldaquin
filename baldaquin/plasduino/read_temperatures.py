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

import struct

import serial

from baldaquin import logger
from baldaquin.plasduino.__arduino__ import pulse_dtr
from baldaquin.plasduino.__serial__ import arduino_info

BAUD_RATE = 115200

port, model, vid, pid = arduino_info()
pulse_dtr(port) # Move to serial interface.
logger.info(f'Opening connection to port {port} at {BAUD_RATE} baud rate...')
interface = serial.Serial()
interface.port = port
interface.baudrate = BAUD_RATE
interface.open()
logger.info('Connection established.')

def sread(size = 1):
    """ Read a given number of bytes from the serial interface.

    Mind the return value is not casted to a python type and None is
    returned upon timeout.
    """
    return interface.read(size)

def sreaduint8():
    """ Read an 8-bit unsigned unsigned integer from the serial port.
    """
    return struct.unpack('>B', sread(1))[0]


a = sreaduint8()
print(a)
