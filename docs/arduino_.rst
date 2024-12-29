:mod:`baldaquin.arduino_` --- Arduino interface
===============================================

This module provides minimal support for interacting with the Arduino ecosystem,
the basic idea is that we start with Arduino UNO and we add on more boards as we
need them.

The :class:`ArduinoBoard <baldaquin.arduino_.ArduinoBoard>` class provides a small
container encapsulating all the information we need to interact with a board, most
notably the list of (vid, pid) for the latter (that can be used to auto-detect
boards attached to a COM port), as well as the relevant parameters to upload sketches
on it. The ``_SUPPORTED_BOARDS`` variable contains a list of boards that we support.
Additional boards can be incrementally added there.


Autodetecting boards
--------------------


Uploading sketches
------------------



Module documentation
--------------------

.. automodule:: baldaquin.arduino_
