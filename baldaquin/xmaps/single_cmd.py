__author__ = 'minuti'
import socket
import time
import struct 
import numpy as np
from matplotlib import pyplot as plt


def sendmsg(socket, TXMessage):
    msglen = struct.pack("<L", (len(TXMessage)))
    #print "going to transmit %d bytes" %len(TXMessage)
    socket.send(msglen)
    #socket.sendall(TXMessage)
    socket.sendall(TXMessage.encode())
   
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


#################################################################################