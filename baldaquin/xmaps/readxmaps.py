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

"""
"""


def SendCmd (cmdlist):
    #############################################################################
    ServerIP = "192.168.0.1"
    ServerPort = 6666
    terminator=''
    for cmd in cmdlist:
        #############################################################################
        if cmd[-1] != '\n':
         terminator = ''
        #############################################################################
        ConnSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
         ConnSocket.connect((ServerIP, ServerPort))
         ConnSocket.settimeout(2)
         ConnSocket.setblocking(1)
        except:
         print (ServerIP + " Not Available :( :(")
        #############################################################################
        sendmsg(ConnSocket, cmd+terminator)
        #############################################################################
        rcvmsg (ConnSocket)


    ConnSocket.close()

#################################################################################

if __name__ == '__main__':
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
