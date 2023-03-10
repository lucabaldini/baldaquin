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
import matplotlib.pyplot as plt
import numpy as np

from baldaquin.xmaps import XMAPS_NUM_COLS, XMAPS_NUM_ROWS
from baldaquin.xmaps.protocol import setup_dac, enable_all_pixels, read_image


__description__ = 'Simple command-line application to read XMAPS'


def connect(ip_address : str, port : int) -> socket.socket:
    """Connect to a socket.
    """
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info(f'Trying to connect to {ip_address} on port {port}...')
    socket_.settimeout(2)
    try:
        socket_.connect((ip_address, port))
        socket_.setblocking(True)
        logger.info('Done, socket connected!')
    except TimeoutError as exception:
        logger.error(f'Cannot connect to server {ip_address} on port {port}')
        raise exception
    return socket_


def main(args):
    """Main entry point for the application.
    """
    socket_ = connect(args.address, args.port)
    setup_dac(socket_)
    enable_all_pixels(socket_)
    data = np.zeros((XMAPS_NUM_COLS, XMAPS_NUM_ROWS), dtype=int)
    for _ in range(args.frames):
        string, payload = read_image(socket_, args.shutter)
        data += np.array(payload).reshape(XMAPS_NUM_COLS, XMAPS_NUM_ROWS) - 1
        np.set_printoptions(linewidth= 160,threshold=2000)
        print(string)
        print(data)

    plt.figure('Image display')
    plt.imshow(data)
    plt.colorbar()
    socket_.close()

    logger.info('Saving data to file...')
    np.save('img.npy', data)

    plt.show()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('--address', type=str, default='192.168.0.1',
        help='the IP address of the server for the socket connection')
    parser.add_argument('--port', type=int, default=6666,
        help='the port for the socket connection')
    parser.add_argument('--shutter', type=int, default=1000000,
        help='the shutter time in us')
    parser.add_argument('--frames', type=int, default=10,
        help='number of frames to be readout')
    main(parser.parse_args())
