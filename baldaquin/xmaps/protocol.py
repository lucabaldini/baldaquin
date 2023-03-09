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



XMAPS_NUM_COLS = 32
XMAPS_NUM_ROWS = 32
XMAPS_NUM_PIXELS = XMAPS_NUM_COLS * XMAPS_NUM_ROWS
XMAPS_IMG_FMT = f'{XMAPS_NUM_PIXELS}B'

DEFAULT_ENCODING = 'utf-8'


class Command(Enum):

    """Definition of the XMAPS valid commands.
    """

    SET_DAC_V = 'SetDACV {arg1:d} {arg2:f}'
    SCAN_COUNTERS = 'XMAPS_Scan_counters {arg1:d} {arg2:d} {arg3:d}'
    APPLY_LOADEN_PULSE = 'XMAPS_Apply_loaden_pulse'
    APPLY_SHUTTER = 'XMAPS_Apply_shutter_us {arg1:d}'



def _read_segment(connected_socket : socket.socket, length : int,
    max_chunck_length : int = 2048, encoding : str = DEFAULT_ENCODING) -> bytes:
    """Read a message segment of a given length.
    """
    received_bytes = 0
    segment = bytes('', encoding)
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
    """
    segment = _read_segment(connected_socket, length)
    data = struct.unpack(fmt, segment)
    # If the segment contain a single value, return that instead of a 1-element tuple.
    if len(data) == 1:
        return data[0]
    return data


def receive_message(connected_socket : socket.socket):
    """Receive a message through an already connected socket.
    """
    total_length = _unpack_segment(connected_socket, 4, '<L')
    string_length = _unpack_segment(connected_socket, 4, '<L')
    string = _read_segment(connected_socket, string_length)
    payload_length = total_length - string_length - 4
    if payload_length == 0:
        return string, None
    fmt = f'{payload_length}B'
    payload = _unpack_segment(connected_socket, payload_length, fmt)
    if payload_length == XMAPS_NUM_PIXELS:
        payload = payload.reshape(XMAPS_NUM_COLS, XMAPS_NUM_ROWS)
    return string, payload


def send_message(connected_socket : socket.socket, message : str,
    encoding : str = DEFAULT_ENCODING) -> None:
    """Send a message through an already connected socket.

    Arguments
    ---------
    connected_socket : socket.socket instance
        The connected socket object that the message must be sent through.

    message : str
        The actual message.

    encoding : str
        The encoding to be used to convert the message into a bytes object.
    """
    # Send the length of the message first, packed as an integer...
    connected_socket.send(struct.pack("<L", len(message)))
    # ...and then the actual message.
    message = message.encode(encoding, errors='strict')
    connected_socket.sendall(message)


def send_command(connected_socket : socket.socket, cmd : Command, **kwargs):
    """Send a command.
    """
    cmd = cmd.value.format(**kwargs)
    cmd = f'{cmd}\n'
    send_message(connected_socket, cmd)
    status, _ = receive_message(connected_socket)
    return status
