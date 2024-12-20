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

import struct

import serial

from baldaquin import logger
from baldaquin.plasduino.protocol import PlasduinoSerialInterface, AnalogReadout
from baldaquin.plasduino.__serial__ import arduino_info


port, model, vid, pid = arduino_info()
interface = PlasduinoSerialInterface(port)
interface.pulse_dtr()
logger.info('Hand-shaking with the arduino board...')
sketch_id = interface.read_uint8()
sketch_version = interface.read_uint8()
logger.info(f'Sketch {sketch_id} version {sketch_version} loaded onboard...')
logger.info('Starting run...')
interface.setup_analog_sampling_sketch((0, 1), 500)
interface.write_start_run()
for i in range(5):
    event = AnalogReadout.unpack(interface.read(8))
    print(event)
interface.write_stop_run()
logger.info('Flushing the serial port...')
data = interface.flush()
print(data)
