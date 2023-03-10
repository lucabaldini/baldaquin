#!/usr/bin/env python3
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

"""Small application to read the XMAPS chip.
"""

import argparse
import socket

from loguru import logger

from baldaquin.xmaps.protocol import send_command, Command


__description__ = 'Simple command-line application to read XMAPS'


def connect(ip_address : str, port : int) -> socket.socket:
    """Connect to a socket.
    """
    connected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'Trying to connect to {ip_address} on port {port}...')
    connected_socket.settimeout(2)
    try:
        connected_socket.connect((ip_address, port))
        connected_socket.setblocking(True)
        logger.info('Done, socket connected!')
    except TimeoutError as exception:
        logger.error(f'Cannot connect to server {ip_address} on port {port}')
        raise exception
    return connected_socket


def main(args):
    """Main entry point for the application.
    """
    connected_socket = connect(args.ip, args.port)
    send_command(connected_socket, Command.SET_DAC_V, buffer=7, value=0.2)
    send_command(connected_socket, Command.SCAN_COUNTERS, arg1=255, arg2=896, arg3=0)
    send_command(connected_socket, Command.APPLY_LOADEN_PULSE)
    send_command(connected_socket, Command.SCAN_COUNTERS, arg1=255, arg2=896, arg3=0)
    send_command(connected_socket, Command.APPLY_SHUTTER, duration=args.shutter)
    send_command(connected_socket, Command.SCAN_COUNTERS, arg1=255, arg2=896, arg3=0)
    connected_socket.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--ip', type=str, default='192.168.0.1',
        help='the IP address of the server for the socket connection')
    parser.add_argument('--port', type=int, default=6666,
        help='the port for the socket connection')
    parser.add_argument('--shutter', type=int, default=1000000,
        help='the shutter time in us')
    main(parser.parse_args())
