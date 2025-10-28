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

"""Plasduino common resources.
"""

from __future__ import annotations

import struct
import time
from typing import Any

from aptapy.plotting import VerticalCursor
from aptapy.strip import StripChart

from baldaquin import arduino_, plasduino
from baldaquin.__qt__ import QtWidgets
from baldaquin.app import UserApplicationBase
from baldaquin.config import UserApplicationConfiguration
from baldaquin.event import EventHandlerBase
from baldaquin.gui import MainWindow, SimpleControlBar
from baldaquin.logging_ import logger
from baldaquin.plasduino.protocol import (
    AnalogReadout,
    DigitalTransition,
    InterruptMode,
    Marker,
    OpCode,
)
from baldaquin.plasduino.sketches import sketch_file_path
from baldaquin.runctrl import RunControlBase
from baldaquin.serial_ import SerialInterface

# List of supported boards, i.e., only the arduino uno at the moment.
_SUPPORTED_BOARDS = (arduino_.UNO, )


class PlasduinoSerialInterface(SerialInterface):

    """Specialized plasduino serial interface.

    This is derived class of our basic serial interface, where we essentially
    implement the simple plasduino communication protocol.
    """

    # pylint: disable=too-many-ancestors

    def read_and_unpack(self, fmt: str) -> Any:
        """Overloaded function.

        For some reason on the arduino side we go into the trouble of reverting the
        native bit order and we transmit things as big endian---I have no idea
        what I was thinking, back in the days, but I don't think it makes sense
        to fix this nonsense, now. Extra work on the transmitting side, and extra
        work on the receiving side too. Good job, Luca!
        """
        return super().read_and_unpack(f">{fmt}")

    def read_sketch_info(self):
        """Read the information about the sketch loaded on the board.

        The sketch information (identifier, version) is the first bit of info that
        the plasduino sketches send out, and this should be the first function
        called after a setup.
        """
        sketch_id = self.read_and_unpack("B")
        sketch_version = self.read_and_unpack("B")
        return sketch_id, sketch_version

    def read_run_end_marker(self) -> None:
        """Read a single byte from the serial port and make sure it is the
        run-end marker.

        (The run end marker is sent over through the serial port from the arduino
        sketch when the run is stopped and all the measurements have been completed,
        and needs to be taken out of the way in order for the next run to take place.)
        """
        logger.info("Waiting for the run end marker...")
        marker = self.read_and_unpack("B")
        if not marker == Marker.RUN_END_MARKER:
            raise RuntimeError(f"Run end marker mismatch "
                  f"(expected {hex(Marker.RUN_END_MARKER)}, found {hex(marker)}).")
        logger.info("Run end marker correctly read.")

    def read_until_run_end_marker(self, timeout: float = None) -> None:
        """Read data from the serial port until the end-of-run marker is found.

        This is actually never used, as the intermediate data would get lost, but
        it is potentially useful when debugging the serial communication.

        Arguments
        ---------
        timeout : float (default None)
            The timeout (in s) to be temporarily set for the transaction.
        """
        logger.info("Scanning serial input for run-end marker...")
        previous_timeout = self.timeout
        if timeout != self.timeout:
            self.timeout = timeout
            logger.debug(f"Serial port timeout temporarily set to {self.timeout} s...")
        data = self.read_until(struct.pack("B", Marker.RUN_END_MARKER))
        if len(data) > 0:
            logger.debug(f"{len(data)} byte(s) found: {data}")
        if previous_timeout != self.timeout:
            self.timeout = previous_timeout
            logger.debug(f"Serial port timeout restored to {self.timeout} s...")

    def write_opcode(self, opcode: OpCode) -> int:
        """Write the value of a given opcode to the serial port.

        This is typically meant to signal the start/stop run, or to configure the
        behavior of the sketch on the arduino side (e.g., select the pins for
        analog readout).

        Arguments
        ---------
        opcode : OpCode
            The operational code to be written to the serial port.
        """
        logger.debug(f"Writing {opcode} to the serial port...")
        return self.pack_and_write(opcode.value, "B")

    def write_start_run(self) -> int:
        """ Write a start run command to the serial port.
        """
        return self.write_opcode(OpCode.OP_CODE_START_RUN)

    def write_stop_run(self) -> int:
        """ Write a stop run command to the serial port.
        """
        return self.write_opcode(OpCode.OP_CODE_STOP_RUN)

    def write_cmd(self, opcode: OpCode, value: int, fmt: str) -> None:
        """ Write a command to the arduino board.

        This implies writing the opcode to the serial port, writing the actual
        payload and, finally, reading back the arduino response and making
        sure the communication went fine.

        And, looking back at this after many years, I cannot help noticing that
        it looks a little bit funny, but I guess it did make sense, back in the
        days.

        Arguments
        ---------
        opcode : OpCode
            The opcode defining the command.

        value : int
            The actual value.

        fmt : str
            The format string.
        """
        self.write_opcode(opcode)
        logger.debug(f"Writing configuration value {value} to the serial port")
        self.pack_and_write(value, fmt)
        target_opcode = self.read_and_unpack("B")
        actual_opcode = self.read_and_unpack("B")
        actual_value = self.read_and_unpack(fmt)
        logger.debug(f"Board response ({target_opcode}, {actual_opcode}, {actual_value})...")
        if actual_opcode != opcode or actual_value != value:
            raise RuntimeError(f"Write/read mismatch in {self.__class__.__name__}.write_cmd()")

    def setup_analog_sampling_sketch(self, pins: list[int], sampling_interval: int) -> None:
        """Setup the `analog_sampling` sketch.

        Note that we are taking a minimal approach, here, where exactly two input
        analog pins are used, and they are those dictated by the Lab 1 shield, i.e.,
        the only thing that we are setting, effectively, is the sampling interval.

        Arguments
        ---------
        sampling_interval : int
            The sampling interval in ms.
        """
        self.write_cmd(OpCode.OP_CODE_SELECT_NUM_ANALOG_PINS, len(pins), "B")
        for pin in pins:
            self.write_cmd(OpCode.OP_CODE_SELECT_ANALOG_PIN, pin, "B")
        self.write_cmd(OpCode.OP_CODE_SELECT_SAMPLING_INTERVAL, sampling_interval, "I")

    def setup_digital_timer_sketch(self, interrupt_mode0, interrupt_mode1) -> None:
        """Setup the `digital_timer` sketch.
        """
        self.write_cmd(OpCode.OP_CODE_SELECT_INTERRUPT_MODE, interrupt_mode0, "B")
        self.write_cmd(OpCode.OP_CODE_SELECT_INTERRUPT_MODE, interrupt_mode1, "B")


class PlasduinoRunControl(RunControlBase):

    """Specialized plasduino run control.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME


class PlasduinoEventHandlerBase(EventHandlerBase):

    """Plasduino basic event handler.

    This takes care of all the operations connected with the handshaking and
    sketch upload. Derived classes must implement the ``read_packet()`` slot.
    """

    # pylint: disable=abstract-method
    SKETCH_ID = None
    SKETCH_VERSION = None

    def __init__(self) -> None:
        """Constructor.

        Note we create an empty serial interface, here, and we then open the port
        while setting up the user application.
        """
        super().__init__()
        self.serial_interface = PlasduinoSerialInterface()

    def open_serial_interface(self, timeout: float = None, handshake_timeout: float = 5.) -> None:
        """Autodetect a supported arduino board, open the serial connection to it,
        and do the handshaking.

        Arguments
        ---------
        timeout : float (default None)
            The timeout (in s) for the serial readout. If set to None, every read
            operation is effectively blocking, and this is the way we should operate
            in normal conditions.

        handshake_timeout : float
            The timeout for the first handshaking with the board, when we try and
            gauge the identifier and version of the sketch that is preloaded.
            Note that this cannot be too small, as it takes a good second for the
            thing to happen.
        """
        port_info = arduino_.autodetect_arduino_board(*_SUPPORTED_BOARDS)
        if port_info is None:
            raise RuntimeError("Could not find a suitable arduino board connected.")
        self.serial_interface.connect(port_info, timeout=timeout)
        self.serial_interface.pulse_dtr()
        logger.info("Hand-shaking with the arduino board...")

        # Temporarily set a finite timeout to handle the case where there is not
        # sensible sketch pre-loaded on the board, and we have to start from scratch.
        self.serial_interface.timeout = handshake_timeout
        try:
            sketch_id, sketch_version = self.serial_interface.read_sketch_info()
            logger.info(f"Sketch {sketch_id} version {sketch_version} loaded onboard...")
        except struct.error:
            logger.warning("There seems to be no plasduino scketch pre-loaded on the board...")
            sketch_id, sketch_version = None, None
        # Now put back the actual target timeout.
        self.serial_interface.timeout = timeout

        # If the sketch uploaded onboard is the one we expect, we're good to go.
        if (sketch_id, sketch_version) == (self.SKETCH_ID, self.SKETCH_VERSION):
            return

        # Otherwise we have to upload the proper sketch.
        file_path = sketch_file_path(self.SKETCH_ID, self.SKETCH_VERSION)
        board = arduino_.ArduinoBoard.by_device_id(port_info.device_id)
        arduino_.upload_sketch(file_path, board.designator, port_info.name)
        sketch_id, sketch_version = self.serial_interface.read_sketch_info()
        if (sketch_id, sketch_version) != (self.SKETCH_ID, self.SKETCH_VERSION):
            raise RuntimeError(f"Could not upload sketch {self.SKETCH_ID} "
                               f"version {self.SKETCH_VERSION}")

    def close_serial_interface(self) -> None:
        """Close the serial interface.
        """
        self.serial_interface.disconnect()


class PlasduinoAnalogEventHandler(PlasduinoEventHandlerBase):

    """Event handler for the plasduino sketches reading analog data.
    """

    SKETCH_ID = 2
    SKETCH_VERSION = 3

    def read_packet(self) -> int:
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(AnalogReadout.size)

    def wait_pending_packets(self, wait_time: int = None) -> int:
        """Wait and read all the pending packets from the serial port, then consume
        the run end marker.

        This is necessary because, after the sketch running on the arduino board
        receives the run end opcode, there is a varible number of analog readouts
        (ranging from 0 to 2 if 2 pins are used) that are acquired before the
        data acquisition is actually stopped. (Yes, poor design on the sketch side.)
        What we do here is essentially: wait a long enough time (it should be
        equal or longer than the sampling time to catch all the corner cases),
        see how many bytes are waiting in the input buffer of the serial port,
        calculate the number of pending packets, read them and finally consume the
        run end marker, so that we are ready to start again.

        Note that the pending packets are correctly processed, passed to the
        event handler buffer and written to disk.

        Arguments
        ---------
        wait_time : int (default None)
            The amount of time (in ms) we wait before polling the serial port
            for additional pending packets.
        """
        logger.info(f"Waiting {wait_time} ms for pending packet(s)...")
        if wait_time is not None:
            time.sleep(wait_time / 1000.)
        num_bytes = self.serial_interface.in_waiting
        # At this point we expect a number of events which is a multiple of
        # AnalogReadout.size, + 1. If this is not the case, it might indicate that
        # we have not waited enough.
        if num_bytes % AnalogReadout.size != 1:
            logger.warning(f"{num_bytes} pending bytes on the serial port, expected 1, 9 or 17...")
        num_packets = num_bytes // AnalogReadout.size
        if num_packets > 0:
            logger.info(f"Reading the last {num_packets} packet(s) from the serial port...")
            for _ in range(num_packets):
                self.acquire_packet()
            self.flush_buffer()
        self.serial_interface.read_run_end_marker()


class PlasduinoDigitalEventHandler(PlasduinoEventHandlerBase):

    """Event handler for the plasduino sketches reading digital data.
    """

    SKETCH_ID = 1
    SKETCH_VERSION = 3

    def read_packet(self):
        """Read a single packet, that is, an analog readout.
        """
        return self.serial_interface.read(DigitalTransition.size)


class PlasduinoAnalogConfiguration(UserApplicationConfiguration):

    """User application configuration for plasduino analog applications.
    """

    _PARAMETER_SPECS = (
        ("strip_chart_max_length", int, 200, "Strip chart maximum length",
            dict(min=10, max=1000000)),
    )


class PlasduinoDigitalConfiguration(UserApplicationConfiguration):

    """User application configuration for plasduino digital applications.
    """

    _PARAMETER_SPECS = ()


class PlasduinoUserApplicationBase(UserApplicationBase):

    """Base class for all the plasduino applications.
    """

    def configure(self):
        """Overloaded method.
        """

    def teardown(self) -> None:
        """Overloaded method (STOPPED -> RESET).
        """
        self.event_handler.close_serial_interface()

    def start_run(self) -> None:
        """Overloaded method (STOPPED -> RUNNING).
        """
        self.event_handler.serial_interface.write_start_run()
        super().start_run()


class PlasduinoAnalogUserApplicationBase(PlasduinoUserApplicationBase):

    """Specialized base class for plasduino user applications relying on the
    `analog_sampling` sketch.
    """

    _PINS = None
    _LABEL = ""
    _SAMPLING_INTERVAL = None
    _ADDITIONAL_PENDING_WAIT = 200

    def __init__(self) -> None:
        """Overloaded Constructor.
        """
        super().__init__()
        if self._PINS is None:
            raise NotImplementedError(f"{self.__class__.__name__} must define _PINS.")
        self.strip_chart_dict = self.create_strip_charts(self._PINS, ylabel=self._LABEL)
        self.axes = None
        self._cursor = None

    @staticmethod
    def create_strip_charts(pins: list[int], ylabel: str = "ADC counts"):
        """Create all the strip charts for displaying real-time data.
        """
        kwargs = dict(xlabel="Time [s]", ylabel=ylabel)
        return {pin: StripChart(label=f"Pin {pin}", **kwargs) for pin in pins}

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()
        self.event_handler.serial_interface.setup_analog_sampling_sketch(self._PINS,
                                                                         self._SAMPLING_INTERVAL)

    def configure(self) -> None:
        """Overloaded method.
        """
        max_length = self.configuration.application_section().value("strip_chart_max_length")
        for chart in self.strip_chart_dict.values():
            chart.set_max_length(max_length)

    def stop_run(self) -> None:
        """Overloaded method (RUNNING -> STOPPED).
        """
        super().stop_run()
        self.event_handler.serial_interface.write_stop_run()
        self.event_handler.wait_pending_packets(self._SAMPLING_INTERVAL +
                                                self._ADDITIONAL_PENDING_WAIT)

    def activate_cursors(self) -> None:
        """Activate vertical cursors on all the strip charts.
        """
        logger.debug("Activating vertical cursor on strip charts...")
        self.axes.clear()
        self._cursor = VerticalCursor(self.axes)
        for chart in self.strip_chart_dict.values():
            chart.plot(self.axes)
            self._cursor.add_marker(chart.spline())
        self.axes.figure.canvas.draw()
        self._cursor.activate()

    def deactivate_cursors(self) -> None:
        """Deactivate vertical cursors on all the strip charts.
        """
        if self._cursor is not None:
            self._cursor.deactivate()
            self._cursor = None


class PlasduinoDigitalUserApplicationBase(PlasduinoUserApplicationBase):

    """Specialized base class for plasduino user applications relying on the
    `digital_timer` sketch.
    """

    def setup(self) -> None:
        """Overloaded method (RESET -> STOPPED).
        """
        self.event_handler.open_serial_interface()
        args = InterruptMode.CHANGE, InterruptMode.DISABLED
        self.event_handler.serial_interface.setup_digital_timer_sketch(*args)

    def stop_run(self) -> None:
        """Overloaded method (RUNNING -> STOPPED).
        """
        super().stop_run()
        self.event_handler.serial_interface.write_stop_run()
        self.event_handler.serial_interface.read_run_end_marker()


class PlasduinoMainWindow(MainWindow):

    """Application graphical user interface.
    """

    _PROJECT_NAME = plasduino.PROJECT_NAME
    _CONTROL_BAR_CLASS = SimpleControlBar
    _UPDATE_INTERVAL = 500

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        """Constructor.
        """
        super().__init__()
        self.hide_reset_button()
        self.strip_chart_tab = self.add_plot_canvas_tab("Strip charts",
                                                        update_interval=self._UPDATE_INTERVAL)
        self.tab_widget.setCurrentWidget(self.strip_chart_tab)

    def setup_user_application(self, user_application):
        """Overloaded method.
        """
        super().setup_user_application(user_application)
        # This line is ugly, and we should find a better way to provide the user
        # application with access to the axes objects in the plotting widgets.
        user_application.axes = self.strip_chart_tab.axes
        self.strip_chart_tab.register(*user_application.strip_chart_dict.values())
