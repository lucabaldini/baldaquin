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

from baldaquin.xmaps import DacChannel, XMAPS_BUFFER_FULL_MASK, XMAPS_NUM_READOUT_CYCLES


_ENCODING = 'utf-8'


class Command(Enum):

    """Definition of the basic commands.
    """

    # Setup the multi-channel DAC.
    #
    # channel -> the DAC channels;
    # value -> the DAC value to be set in V.
    SET_DAC = 'SetDACV {channel:d} {value:f}'

    # Scan the pixel counters circulating a token across specific buffers/pixels.
    #
    # mask -> an 8-bit mask (0--255) mapping the readout buffers;
    # cycles -> the number of clock cycles (typically 128 channels x 7 bits = 896) per buffer;
    # din -> the d_in value (0 is enable, and 1 is disable).
    SCAN_COUNTERS = 'XMAPS_Scan_counters {mask:d} {cycles:d} {din:d}'

    # Load the proper values (circulated via a SCAN_COUNTER call) in the pixel registers.
    # (This takes no argument.)
    PULSE_COUNTERS = 'XMAPS_Apply_loaden_pulse'

    # Read the pixel counter.
    #
    # mask -> an 8-bit mask (0--255) mapping the readout buffers;
    # din -> obsolete, as in a READ_COUNTERS call this has to be 0. (Will be removed.)
    READ_COUNTERS = 'XMAPS_Read_counters {mask:d} {din:d}'

    # Open the shutter signal for a pre-defined period of time.
    #
    # duration -> the shutter duration in us.
    OPEN_SHUTTER = 'XMAPS_Apply_shutter_us {duration:d}'



def _read_segment(socket_ : socket.socket, length : int,
    max_chunck_length : int = 2048) -> bytes:
    """Read a message segment of a given length.

    Arguments
    ---------
    socket_ : socket.socket instance
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
        data = socket_.recv(chunck_length)
        segment += data
        received_bytes += len(data)
    return segment


def _unpack_segment(socket_ : socket.socket, length : int, fmt : str) -> int:
    """Unpack a message segment of a given length.

    Note that, according to the documentation of struc.unpack(), the result is a
    tuple even if it contains exactly one item, and therefore when the length of
    the unpacked data is one, we return the (only) element of the tuple, instead.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.

    length : int
        The length of the message segment to be read in bytes.

    fmt : str
        The format string to be passed to struct.unpack().
    """
    segment = _read_segment(socket_, length)
    data = struct.unpack(fmt, segment)
    # If the segment contain a single value, return that instead of a 1-element tuple.
    if len(data) == 1:
        return data[0]
    return data


def receive_message(socket_ : socket.socket):
    """Receive a message through an already connected socket.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.
    """
    total_length = _unpack_segment(socket_, 4, '<L')
    string_length = _unpack_segment(socket_, 4, '<L')
    string = _read_segment(socket_, string_length)
    logger.debug(f'Message string received: "{string}"')
    payload_length = total_length - string_length - 4
    if payload_length == 0:
        return string, None
    fmt = f'{payload_length}B'
    payload = _unpack_segment(socket_, payload_length, fmt)
    return string, payload


def send_message(socket_ : socket.socket, message : str) -> None:
    """Send a message through an already connected socket.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.

    message : str
        The actual message.
    """
    logger.debug(f'Sending message "{message}"...')
    # Send the length of the message first, packed as an integer...
    socket_.send(struct.pack("<L", len(message)))
    # ...and then the actual message.
    message = message.encode(_ENCODING, errors='strict')
    socket_.sendall(message)


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


def send_command(socket_ : socket.socket, command : Command, terminator : str = '\n', **kwargs):
    """Send a command.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.

    command : Command enum value
        The command to be sent.

    terminator : string, optional
        The optional line terminator to be attached at the end of the string.

    **kwargs
        The named values for all the command parameters.
    """
    send_message(socket_, format_command(command, terminator, **kwargs))
    return receive_message(socket_)


def setup_dac(socket_ : socket.socket, ibias : float = 3.3, ibr : float = 1.4,
    vtest : float = 0.) -> None:
    """Setup the multi-channel DAC for the peripheral pixels.

    Note that all the unused channels are set to 0.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.

    ibias : float
        The value for the IBIAS DAC channel in V.

    ibr : float
        The value for the IBR DAC channel in V.

    vtest : float
        The value for the VTEST DAC channel in V.
    """
    send_command(socket_, Command.SET_DAC, channel=DacChannel.IBIAS, value=ibias)
    send_command(socket_, Command.SET_DAC, channel=DacChannel.IBR, value=ibr)
    send_command(socket_, Command.SET_DAC, channel=DacChannel.VTEST, value=vtest)
    for channel in DacChannel.unused_channels():
        send_command(socket_, Command.SET_DAC, channel=channel, value=0.)


def enable_all_pixels(socket_ : socket.socket):
    """Enable all the pixels for counting.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.
    """
    send_command(socket_, Command.SCAN_COUNTERS, mask=XMAPS_BUFFER_FULL_MASK,
        cycles=XMAPS_NUM_READOUT_CYCLES, din=0)
    send_command(socket_, Command.PULSE_COUNTERS)


def read_image(socket_ : socket.socket, shutter_time : int):
    """Read a full image.

    Arguments
    ---------
    socket_ : socket.socket instance
        The connected socket object that the message must be sent through.
    """
    send_command(socket_, Command.OPEN_SHUTTER, duration=shutter_time)
    return send_command(socket_, Command.READ_COUNTERS, mask=XMAPS_BUFFER_FULL_MASK, din=0)
