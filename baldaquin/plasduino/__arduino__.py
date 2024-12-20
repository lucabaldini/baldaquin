# Copyright (C) 2024 the baldaquin team.
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

import serial
import time

from baldaquin import logger

# import os
# import re
# import sys
# import glob
#
# from plasduino.__plasduino__ import PLASDUINO_ARDUINO
# from plasduino.__logging__ import logger, abort
# from plasduino.arduino.sketches_h import *
#
#
# HEADER_FILES = glob.glob(os.path.join(PLASDUINO_ARDUINO, '*.h'))
#
# SUPPORTED_BOARDS = ['uno', 'atmega328diecimila168']
#
#

def pulse_dtr(port: str) -> None:
    """ Assert the DTR for 0.5 s on the specified port and then de-assert it.
    """
    logger.info('Pulsing serial control line...')
    ser = serial.Serial(port)
    ser.setDTR(1)
    time.sleep(0.5)
    ser.setDTR(0)
    ser.close()

# def getHexFileName(sketchName, board):
#     """ Return the file name for the binary file of the sketch compile for a
#     given board.
#     """
#     return '%s-%s.hex' % (sketchName, board)
#
# def getSketchInfo(sketchName):
#     """ Open the sketch (.ino) file and figure out the sketch id and version.
#     """
#     fileName = '%s.ino' % sketchName
#     filePath = os.path.join(PLASDUINO_ARDUINO, sketchName, fileName)
#     content = open(filePath, 'r').read()
#     try:
#         sketchId = re.search('(?<=SKETCH_ID).+', content).group(0)
#         sketchId = eval(sketchId)
#     except:
#         logger.warn('Could not retrieve sketch ID for %s.' % sketchName)
#         sketchId = None
#     try:
#         sketchVersion =\
#             re.search('(?<=SKETCH_VERSION).+', content).group(0).strip()
#         sketchVersion = int(sketchVersion)
#     except:
#         logger.warn('Could not retrieve sketch version for %s.' % sketchName)
#         sketchVersion = None
#     return sketchId, sketchVersion
#
# def listSketches():
#     """ List all the sketches available for upload.
#     """
#     sketchList = []
#     for folderPath in glob.glob(os.path.join(PLASDUINO_ARDUINO, '*')):
#         if os.path.isdir(folderPath):
#             sketchName = os.path.basename(folderPath)
#             if glob.glob(os.path.join(folderPath, '*.hex')):
#                 sketchList.append(sketchName)
#     sketchList.sort()
#     return sketchList
#
#
#
# if __name__ == '__main__':
#     for item in dir():
#         if item.isupper():
#             print('%s = %s' % (item, eval(item)))
#     for sketchName in listSketches():
#         try:
#             print('%s version: %s' % (sketchName, getSketchInfo(sketchName)))
#         except:
#             print('*** Cannot determine info for %s.' % sketchName)
