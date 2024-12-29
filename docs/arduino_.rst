:mod:`baldaquin.arduino_` --- Arduino interface
===============================================

This module provides minimal support for interacting with the Arduino ecosystem,
the basic idea is that we start with Arduino UNO and we add on more boards as we
need them.

The :class:`ArduinoBoard <baldaquin.arduino_.ArduinoBoard>` class provides a small
container encapsulating all the information we need to interact with a board, most
notably the list of (vid, pid) for the latter (that can be used to auto-detect
boards attached to a COM port), as well as the relevant parameters to upload sketches
on it.

The ``_SUPPORTED_BOARDS`` variable contains a list of boards that we support.
Additional boards can be incrementally added there.


Auto-detecting boards
---------------------

The module comes with a few utilities to help auto-detecting boards.

:meth:`board_identifiers() <baldaquin.arduino_.board_identifiers>` builds all
the ``(vid, pid)`` pairs corresponding to the :class:`ArduinoBoard <baldaquin.arduino_.ArduinoBoard>`
objects passed as an argument, e.g.,

>>> arduino_.board_identifiers(arduino_.UNO)
>>>
>>> ((0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x2341, 0x0243), (0x2341, 0x006A))

This, in turn, can be used to filter the devices connected to the COM ports in
order to auto-discover specific boards.

:meth:`identify_arduino_board() <baldaquin.arduino_.identify_arduino_board>` returns
the fully-fledged :class:`ArduinoBoard <baldaquin.arduino_.ArduinoBoard>` object
corresponding to a given (vid, pid):

>>> arduino_.identify_arduino_board(0x2341, 0x0043)
>>>
>>> ArduinoBoard(board_id='uno', name='Arduino UNO', vendor='arduino', architecture='avr',
>>> upload_protocol='arduino', upload_speed=115200, build_mcu='atmega328p',
>>> identifiers=((9025, 67), (9025, 1), (10755, 67), (9025, 579), (9025, 106)))

The two are used in conjunction with the :mod:`baldaquin.serial_` module in the
top-level interfaces
:meth:`autodetect_arduino_boards() <baldaquin.arduino_.autodetect_arduino_boards>`
and :meth:`autodetect_arduino_board() <baldaquin.arduino_.autodetect_arduino_board>`,
which can be integrated into a generic auto-detection workflow.


Uploading sketches
------------------



Module documentation
--------------------

.. automodule:: baldaquin.arduino_
