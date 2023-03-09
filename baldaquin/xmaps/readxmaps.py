# Copyright (C) 2022 the baldaquin team.
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

"""Small module to read XMAPS, adapted from the original script by Massimo.
"""


import socket
import time
import struct
import numpy as np
from matplotlib import pyplot as plt


DEFAULT_ENCODING = utf-8'


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
    connected_socket.sendall(message.encode(encoding, errors='strict'))


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
    """
    """
    segment = _read_segment(connected_socket, length)
    return struct.unpack_from(fmt, segment)[0]


def receive_message(connected_socket : socket.socket):
    """Receive a message through an already connected socket.
    """
    total_length = _unpack_segment(connected_socket, 4, '<L')
    string_length = _unpack_segment(connected_socket, 4, '<L')
    string = _read_segment(connected_socket, string_length)
    payload_length = total_len - string_length - 4
    if payload_length > 0:
        payload = _read_segment(connected_socket, payload_length)





def rcvmsg (socket):
##################receiveing TotalLen##################
                received_bytes = 0
                msg_len_str = bytes('', 'utf8')
                while received_bytes < 4:
                        data = socket.recv(4 - received_bytes)
                        msg_len_str = msg_len_str + data
                        received_bytes += len(data)
                msg_len = struct.unpack_from("<L", msg_len_str)[0]
                #print ("going to collect %d total bytes" % msg_len)
                ##################receiveing StrLen##################
                received_bytes = 0
                str_len_str = bytes('', 'utf8')
                while received_bytes < 4:
                    data = socket.recv(4 - received_bytes)
                    str_len_str = str_len_str + data
                    received_bytes += len(data)
                str_len = struct.unpack_from("<L", str_len_str)[0]
                #print ("going to collect %d String bytes" % str_len)
                ##################receiveing MsgStr##################
                str_msg_acc = bytes('', 'utf8')
                received_bytes = 0
                while received_bytes < str_len:
                    if int((str_len - received_bytes) / 2048):
                        data = socket.recv(2048)
                    else:
                        data = socket.recv(str_len - received_bytes)
                    str_msg_acc = str_msg_acc + data
                    received_bytes += len(data)
                #print (str_msg_acc)
                ##################receiveing Bynary##################
                #remember that total len indicates strlen+binarylen+4 bytes for strlen
                binary_len=int(msg_len-str_len-4)
                if binary_len>0:
                    bin_msg_acc = bytes('', 'utf8')
                    received_bytes = 0
                    #print ("going to collect %d Binary bytes" % (binary_len))
                while received_bytes < str_len:
                    if int((binary_len - received_bytes)) / 2048:
                        data = socket.recv(2048)
                    else:
                        data = socket.recv(binary_len - received_bytes)
                    bin_msg_acc = bin_msg_acc + data
                    received_bytes += len(data)

                if binary_len<=0:
                    print(str(str_msg_acc))
                else:
                    a = struct.unpack('1024B',bin_msg_acc)
                    a = np.array(a).reshape(32,32)
                    np.set_printoptions(linewidth= 160,threshold=2000)
                    print (a)
                    print ("AVG:" + str(np.average(a)))
                    print("Mixed Message %s binary len=%s" %(str_msg_acc,len(bin_msg_acc)))
                    imageplot = plt.imshow(a)
                    plt.colorbar()
                    plt.show()

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
