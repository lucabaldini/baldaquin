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

import socket

from loguru import logger

from baldaquin.xmaps.protocol import send_command



def connect(ip : str, port : int) -> socket.socket:
    """Connect to a socket.
    """
    connected_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connected_socket.connect((ip, port))
        # These seem in contradiction, as setblocking(1) is equivalent to settimeout(None)?
        connected_socket.settimeout(2)
        connected_socket.setblocking(1)
    except:
        logger.error(f'Cannot connect to server {ip} on port {port}')
    return connected_socket









if __name__ == '__main__':

    ServerIP = "192.168.0.1"
  ServerPort = 6666


  cmdlist = []
  cmdlist.append("! SetDACV 0 .0\n")
  cmdlist.append("! SetDACV 1 .0\n")
  cmdlist.append("! SetDACV 2 .0\n")
  cmdlist.append("! SetDACV 3 .0\n")
  cmdlist.append("! SetDACV 4 2.2\n")#ibias
  cmdlist.append("! SetDACV 5 1.4\n")#ibr
  cmdlist.append("! SetDACV 6 .0\n")
  cmdlist.append("SetDACV 7 0.2\n")#vtest

  cmdlist.append("XMAPS_Scan_counters 255 896 0\n") #enable all
  #cmdlist.append("XMAPS_Scan_counters 255 882 1\n") #enable few

  cmdlist.append("XMAPS_Apply_loaden_pulse\n")

  cmdlist.append("XMAPS_Scan_counters 255 896 0\n") #reset run

  cmdlist.append("XMAPS_Apply_shutter_us 8000000\n") #count

  cmdlist.append("XMAPS_Read_counters 255 0\n") #readout

  #cmdlist.append("XMAPS_Apply_write_pulses 100000\n") #readout

  #cmdlist.append("XMAPS_Scan_counters 0 1 0\n") #fake inc

  #cmdlist.append("XMAPS_Scan_counters 255 896 0\n") #readout


  SendCmd (cmdlist)
  ConnSocket.close()
