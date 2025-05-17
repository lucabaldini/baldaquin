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
    (This will literally run a script and copy the executable on your machine,
    which is handy because you will not need administrator priviledges to
    run the thing. The same thing holds for all the additional modules, e.g.,
    `arduino:avr` you might need.)


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

As already said earlier on, we shall assume that ``arduino-cli`` is the preferred
way to do business. In most cases you can simply use the top-level interface
:meth:`upload_sketch() <baldaquin.arduino_.upload_sketch>` to upload a sketch onto
an Arduino board connected to the computer.

The baldaquin command-line interface provides a target to manually compile a sketch
to an arduino board

.. code-block:: shell

   [lbaldini@nblbaldini baldaquin]$ python baldaquin/cli.py arduino-upload --help
   usage: cli.py arduino-upload [-h] [--board-designator BOARD_DESIGNATOR]
                                file_path

   positional arguments:
     file_path             the path to the compiled sketch file

   options:
     -h, --help            show this help message and exit
     --board-designator BOARD_DESIGNATOR


Compiling sketches
------------------

The module also provides a way to compile sketches, using the simple, top-level
interface :meth:`compile_sketch() <baldaquin.arduino_.compile_sketch()>`.

The baldaquin command-line interface provides a target to manually compile a sketch
to an arduino board

.. code-block:: shell

   [lbaldini@nblbaldini baldaquin]$ python baldaquin/cli.py arduino-compile --help
   usage: cli.py arduino-compile [-h] [--output_dir OUTPUT_DIR]
                                 [--board_designator BOARD_DESIGNATOR]
                                 file_path

   positional arguments:
     file_path             the path to the sketch source file

   options:
     -h, --help            show this help message and exit
     --output_dir OUTPUT_DIR
     --board_designator BOARD_DESIGNATOR

Note that, depending on the particular sketch you are trying to compile, you might
need additional external library not bundled in the initial ArduinoCli installation.
You find all the necessary resources about libraries in arduino at the
`docs page <https://arduino.github.io/arduino-cli/0.20/commands/arduino-cli_lib/>`_,
but in a nutshell, you can search for specific libraries by doing

.. code-block:: shell

  [lbaldini@nblbaldini baldaquin]$ arduino-cli lib search HTS221
  Name: "Adafruit HTS221"
    Author: Adafruit
    Maintainer: Adafruit <info@adafruit.com>
    Sentence: Arduino library for the HTS221 sensors in the Adafruit shop
    Paragraph: Arduino library for the HTS221 sensors in the Adafruit shop
    Website: https://github.com/adafruit/Adafruit_HTS221
    Category: Sensors
    Architecture: *
    Types: Contributed
    Versions: [0.1.0, 0.1.1, 0.1.2, 0.1.4, 0.1.5]
    Dependencies: Adafruit Unified Sensor, Adafruit BusIO
  Name: "Arduino_HTS221"
    Author: Arduino
    Maintainer: Arduino <info@arduino.cc>
    Sentence: Allows you to read the temperature and humidity sensors of your Nano 33 BLE Sense.
    Paragraph:
    Website: http://github.com/arduino-libraries/Arduino_HTS221
    Category: Sensors
    Architecture: *
    Types: Arduino
    Versions: [1.0.0]
    Provides includes: Arduino_HTS221.h
  Name: "FaBo 208 Humidity HTS221"
    Author: FaBo<info@fabo.io>
    Maintainer: Akira Sasaki<akira@fabo.io>
    Sentence: A library for FaBo Humidity I2C Brick
    Paragraph: HTS221 is humidity and temperature sensor.
    Website: https://github.com/FaBoPlatform/FaBoHumidity-HTS221-Library
    Category: Sensors
    Architecture: avr
    Types: Contributed
    Versions: [1.0.0]
  Name: "STM32duino HTS221"
    Author: AST, Wi6Labs
    Maintainer: stm32duino
    Sentence: Capacitive digital sensor for relative humidity and temperature.
    Paragraph: This library provides Arduino support for the capacitive digital sensor for relative humidity and temperature HTS221 for STM32 boards.
    Website: https://github.com/stm32duino/HTS221
    Category: Sensors
    Architecture: *
    Types: Contributed
    Versions: [1.0.1, 1.0.2, 1.0.3, 1.0.4, 2.0.0, 2.0.1]
  Name: "SmartEverything HTS221"
    Author: Seve
    Maintainer: axelelettronica <development@axelelettronica.it>
    Sentence: Library code for HTS221 Capacitive digital sensor for relative humidity and temperature
    Paragraph: The HTS221 is an ultra compact sensor for relative humidity and temperature.<br>It includes a sensing element and a mixed signal ASIC to provide the measurement information through digital serial interfaces.<br>The sensing element consists of a polymer dielectric planar capacitor structure capable of detecting relative humidity variations and is manufactured using a dedicated ST process.<br>The HTS221 is available in a small top-holed cap land grid array (HLGA) package guaranteed to operate over a temperature range from -40 °C to +120 °C.
    Website: https://github.com/ameltech/sme-hts221-library
    Category: Sensors
    Architecture: *
    Types: Contributed
    Versions: [1.0.0, 1.1.0, 1.1.1, 1.1.2]
  Name: "Sodaq_HTS221"
    Author: Alex Tsamakos,SODAQ
    Maintainer: Alex Tsamakos,SODAQ
    Sentence: An Arduino library for the HTS221 sensor.
    Paragraph: Supports humidity and temperature sensors.
    Website: https://github.com/SodaqMoja/Sodaq_HTS221
    Category: Sensors
    Architecture: *
    Types: Contributed
    Versions: [1.0.0]

and then install the one that you need via

.. code-block:: shell

  [lbaldini@nblbaldini baldaquin]$ arduino-cli lib install "STM32duino HTS221"
  Downloading STM32duino HTS221@2.0.1...
  STM32duino HTS221@2.0.1 downloaded
  Installing STM32duino HTS221@2.0.1...
  Installed STM32duino HTS221@2.0.1



Module documentation
--------------------

.. automodule:: baldaquin.arduino_
