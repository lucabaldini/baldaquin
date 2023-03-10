# Copyright (C) 2023 the baldaquin team.
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

"""Basic definition of the XMAP communication protocol.
"""

from enum import Enum
import socket
import struct

from loguru import logger

from baldaquin.xmaps import XMAPS_NUM_COLS, XMAPS_NUM_ROWS, XMAPS_NUM_PIXELS


_ENCODING = 'utf-8'


class Command(Enum):

    """Definition of the XMAPS valid commands.
    """

    SET_DAC_V = 'SetDACV {buffer:d} {value:f}'
    SCAN_COUNTERS = 'XMAPS_Scan_counters {arg1:d} {arg2:d} {arg3:d}'
    APPLY_LOADEN_PULSE = 'XMAPS_Apply_loaden_pulse'
    APPLY_SHUTTER = 'XMAPS_Apply_shutter_us {duration:d}'



def _read_segment(connected_socket : socket.socket, length : int,
    max_chunck_length : int = 2048) -> bytes:
    """Read a message segment of a given length.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.

    length : int
        The length of the message segment to be read in bytes.

    max_chunck_length : int
        The maximum size of the chunks to be read.
    """
    received_bytes = 0
    segment = bytes('', _ENCODING)
    while received_bytes < length:
        chunck_length = min(length - received_bytes, max_chunck_length)
        data = connected_socket.recv(chunck_length)
        segment += data
        received_bytes += len(data)
    return segment


def _unpack_segment(connected_socket : socket.socket, length : int, fmt : str) -> int:
    """Unpack a message segment of a given length.

    Note that, according to the documentation of struc.unpack(), the result is a
    tuple even if it contains exactly one item, and therefore when the length of
    the unpacked data is one, we return the (only) element of the tuple, instead.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.

    length : int
        The length of the message segment to be read in bytes.

    fmt : str
        The format string to be passed to struct.unpack().
    """
    segment = _read_segment(connected_socket, length)
    data = struct.unpack(fmt, segment)
    # If the segment contain a single value, return that instead of a 1-element tuple.
    if len(data) == 1:
        return data[0]
    return data


def receive_message(connected_socket : socket.socket):
    """Receive a message through an already connected socket.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.
    """
    total_length = _unpack_segment(connected_socket, 4, '<L')
    string_length = _unpack_segment(connected_socket, 4, '<L')
    string = _read_segment(connected_socket, string_length)
    logger.debug(f'Message string received: "{string}"')
    payload_length = total_length - string_length - 4
    if payload_length == 0:
        return string, None
    fmt = f'{payload_length}B'
    payload = _unpack_segment(connected_socket, payload_length, fmt)
    if payload_length == XMAPS_NUM_PIXELS:
        payload = payload.reshape(XMAPS_NUM_COLS, XMAPS_NUM_ROWS)
    return string, payload


def send_message(connected_socket : socket.socket, message : str) -> None:
    """Send a message through an already connected socket.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.

    message : str
        The actual message.
    """
    logger.debug(f'Sending message "{message}"...')
    # Send the length of the message first, packed as an integer...
    connected_socket.send(struct.pack("<L", len(message)))
    # ...and then the actual message.
    message = message.encode(_ENCODING, errors='strict')
    connected_socket.sendall(message)


def format_command(command : Command, terminator : str = '\n', **kwargs):
    """Properly format a given command as a string so that it can be sent over a socket.

    Arguments
    ---------
    command : Command enum value
        The command to be fomatted

    terminator : string, optional
        The optional line terminator to be attached at the end of the string.

    **kwargs
        The named values for all the command parameters.
    """
    command = command.value.format(**kwargs)
    if terminator:
        command = f'{command}{terminator}'
    return command


def send_command(connected_socket : socket.socket, command : Command,
    terminator : str = '\n', **kwargs):
    """Send a command.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.

    command : Command enum value
        The command to be sent.

    terminator : string, optional
        The optional line terminator to be attached at the end of the string.

    **kwargs
        The named values for all the command parameters.
    """
    send_message(connected_socket, format_command(command, terminator, **kwargs))
    return receive_message(connected_socket)
