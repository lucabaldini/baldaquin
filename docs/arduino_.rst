:mod:`baldaquin.arduino_` --- Arduino interface
===============================================

This module provides minimal support for interacting with the Arduino ecosystem,
the basic idea is that we start with Arduino UNO and we add on more boards as we
need them.

.. seealso::

    In order to fully utilize the facilities in this module you will need
    at least some additional third-paryt software. The following links are 
    relevant for operating with Arduino boards. 

    * `Arduino <https://www.arduino.cc/>`_
    * `Arduino CLI <https://arduino.github.io/arduino-cli/>`_
    * `avrdude <https://www.nongnu.org/avrdude/>`_

    Since nowadays the Arduino CLI seems to be the preferred way to interact 
    programmatically with the Arduino ecosystem, we will assume that is the 
    default choice. If you have ``arduino-cli`` installed you should be good to 
    go---see the `installation instructions <https://arduino.github.io/arduino-cli/latest/installation/>`_.


The :class:`ArduinoBoard <baldaquin.arduino_.ArduinoBoard>` class provides a small
container encapsulating all the information we need to interact with a board, most
notably the list of :class:`DeviceId <baldaquin.serial_.DeviceId>` for the latter
(that can be used to auto-detect boards attached to a COM port), as well as the
relevant parameters to upload sketches on it.

A small database internal to the class contains a list of boards that we support,
and which can be retrieved either by DeviceId or by designator:

>>> board = ArduinoBoard.by_device_id(DeviceId(0x2341, 0x43))
>>> print(board)
ArduinoBoard(designator='uno', name='Arduino UNO', vendor='arduino',
    architecture='avr', upload_protocol='arduino', upload_speed=115200,
    build_mcu='atmega328p', device_ids=((vid=0x2341, pid=0x43),
    (vid=0x2341, pid=0x1), (vid=0x2a03, pid=0x43), (vid=0x2341, pid=0x243), 
    (vid=0x2341, pid=0x6a)))
>>>
>>> board = ArduinoBoard.by_designator('uno')
>>> print(board)
ArduinoBoard(designator='uno', name='Arduino UNO', vendor='arduino',
    architecture='avr', upload_protocol='arduino', upload_speed=115200,
    build_mcu='atmega328p', device_ids=((vid=0x2341, pid=0x43),
    (vid=0x2341, pid=0x1), (vid=0x2a03, pid=0x43), (vid=0x2341, pid=0x243), 
    (vid=0x2341, pid=0x6a)))



Auto-detecting boards
---------------------

The module comes with a couple of utilities to help auto-detecting boards.

:meth:`autodetect_arduino_boards() <baldaquin.arduino_.autodetect_arduino_boards>`
will look over all the COM ports and identify all the supported Arduino boards
connected. An arbitrary number of board objects can be passed to the function, and
they will act as a filter for the boards that are actually returned. If, e.g., 
you are interested in all the Arduino UNOs connected, you can do something along 
the lines of:

>>> ports = arduino_.autodetect_arduino_boards(arduino_.UNO)
>>> [INFO] Autodetecting Arduino boards ['Arduino UNO']...
>>> [INFO] Scanning serial devices...
>>> [DEBUG] Port(name='/dev/ttyS0', device_id=(vid=None, pid=None), manufacturer=None)
>>> [DEBUG] Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [INFO] Done, 2 device(s) found.
>>> [INFO] Filtering port list for specific devices: [(vid=0x2341, pid=0x43), (vid=0x2341, pid=0x1), (vid=0x2a03, pid=0x43), (vid=0x2341, pid=0x243), (vid=0x2341, pid=0x6a)]...
>>> [INFO] Done, 1 device(s) remaining.
>>> [DEBUG] Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [DEBUG] /dev/ttyACM0 -> uno (Arduino UNO)
>>> 
>>> print(ports)
>>> [Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')]

The function returns a list of :class:`Port <baldaquin.serial_.Port>` objects,
that are ready to use.

In many cases you might be interested in a single board, in which case you can use
the :meth:`autodetect_arduino_board() <baldaquin.arduino_.autodetect_arduino_board>`,
variant. This will return the first board that is found, and log a warning if 
more than one is connected.

These two functions can be integrated in complex workflows as needed.


Uploading sketches
------------------

This module implements two diffent interfaces to programmatically upload sketches
onto a connected Arduino board:

* :class:`ArduinoCli <baldaquin.arduino_.ArduinoCli>`, wrapping the Arduino
  command-line interface;
* :class:`AvrDude <baldaquin.arduino_.AvrDude>`, wrapping avrdude.

As alerady said earlier on, we shall assume that ``arduino-cli`` is the preferred 
way to do business. In most cases you can simply use the top-level interface 
:meth:`upload_sketch() <baldaquin.arduino_.upload_sketch>` to upload a sketch onto
an Arduino board connected to the computer.


Compiling sketches
------------------



Module documentation
--------------------

.. automodule:: baldaquin.arduino_
