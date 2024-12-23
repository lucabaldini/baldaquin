:mod:`baldaquin.serial_` --- Serial port interface
==================================================

The module provides basically two thing, both of which are light wrappers over the
corresponding `pyserial <https://pyserial.readthedocs.io/en/latest/index.html>`_
functionalities

* :class:`SerialInterface <baldaquin.serial_.SerialInterface>` is a class to
  interface to the serial port;
* :meth:`list_com_ports() <baldaquin.serial_.list_com_ports>` is a function to
  list the available devices connected to the available serial ports (this is
  handy for auto-recognition).


Module documentation
--------------------

.. automodule:: baldaquin.serial_
