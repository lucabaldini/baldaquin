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



"""DAQ control for XMAPS.
"""

import socket

from loguru import logger
import numpy as np

from baldaquin.app import UserApplicationBase
from baldaquin.event import EventHandlerBase
from baldaquin.runctrl import RunControl
from baldaquin.xmaps import XMAPS_NUM_COLS, XMAPS_NUM_ROWS
from baldaquin.xmaps.protocol import setup_dac, enable_all_pixels, read_image


class XmapEventHandler(EventHandlerBase):

    """
    """


class XmapsUserApp(UserApplicationBase):

    """
    """

    EVENT_HANDLER_CLASS = XmapEventHandler

    def __init__(self, address, port):
        """
        """
        super().__init__()
        self.socket_ = None
        self.address = address
        self.port = port

    def setup(self):
        """
        """
        self.socket_ = self.connect(self.address, self.port)
        setup_dac(self.socket_)
        enable_all_pixels(self.socket_)

    @staticmethod
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

    def process_event(self):
        """
        """
        string, payload = read_image(self.socket_, 1000000)
        data = np.array(payload).reshape(XMAPS_NUM_COLS, XMAPS_NUM_ROWS) - 1
        np.set_printoptions(linewidth= 160,threshold=2000)
        print(string)
        print(data)
        return data



class XmapsRunControl(RunControl):

    """Specialized XMAPS run control.
    """




if __name__ == '__main__':
    import os
    import time
    from baldaquin import BALDAQUIN_DATA
    file_path = os.path.join(BALDAQUIN_DATA, 'test_xmaps.bin')
    app = XmapsUserApp('192.168.0.1', 6666)
    rc = XmapsRunControl()
    rc.set_user_application(app)
    rc.set_stopped()
    rc.set_running()

    """
    app.setup()
    app.start(file_path)
    time.sleep(5)
    app.stop()
    """
