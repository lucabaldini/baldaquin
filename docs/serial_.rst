:mod:`baldaquin.serial_` --- Serial interface
=============================================

The module provides basically an abstraction layer over the
`pyserial <https://pyserial.readthedocs.io/en/latest/index.html>`_
package.

The :class:`DeviceId <baldaquin.serial_.DeviceId>` class is a simple class
grouping the vendor and product IDs of a device into a single data structure. The
:class:`Port <baldaquin.serial_.Port>` class represents a serial port, and groups
the  most useful things out of the
`ListPortInfo <https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo>`_
class from pyserial.

The most useful bit in the module is probably the
:meth:`list_com_ports() <baldaquin.serial_.list_com_ports>`, listing all the COM
ports, along wit the device that are attached to them.

>>> ports = serial_.list_com_ports()
>>> [INFO] Scanning serial devices...
>>> [DEBUG] PortInfo(name='/dev/ttyS0', device_id=(vid=None, pid=None), manufacturer=None)
>>> [DEBUG] PortInfo(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [INFO] Done, 2 device(s) found.

The method allows to filter over device IDs (or, equivalently, over vid, pid tuples)
which comes handy when one is interested in a particular device or set of devices.

>>> ports = serial_.list_com_ports((0x2341, 0x0043))
>>> [INFO] Scanning serial devices...
>>> [DEBUG] PortInfo(name='/dev/ttyS0', device_id=(vid=None, pid=None), manufacturer=None)
>>> [DEBUG] PortInfo(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [INFO] Done, 2 device(s) found.
>>> [INFO] Filtering port list for specific devices: [(vid=0x2341, pid=0x43)]...
>>> [INFO] Done, 1 device(s) remaining.
>>> [DEBUG] PortInfo(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')


In addition, the :class:`SerialInterface <baldaquin.serial_.SerialInterface>`
acts like a base class that can be subclassed to implement any specific
communication protocol over the serial port. It is a simple wrapper around the
`pyserial <https://pyserial.readthedocs.io/en/latest/index.html>`_ ``Serial`` class
and provides a few convenience methods to read and write data over the serial port.
The class is designed to be instantiated with no arguments, with the actual connection
to the serial port being done via the
:meth:`SerialInterface.connect() <baldaquin.serial_.SerialInterface.connect()>`
method, e.g.

>>> interface = SerialInterface()
>>> port_info = serial_.list_com_ports()[0]
>>> interface.connect(port_info, baudrate=115200, timeout=1)

Although we generally prefer to exchange fixed-width binary data over the
serial port, we recognize that situations exist where it is more convenient to
talk text, and we provide the :class:`TextLine <baldaquin.serial_.TextLine>` class
to facilitate text-based exchange of numerical, string, or mixed data. The basic
idea is that devices connected over the serial port can pass along line-feed terminated
text strings with a proper header, and where the different fields are separated by
a given character, and the
:meth:`SerialInterface.read_text_line() <baldaquin.serial_.SerialInterface.read_text_line()>`
is equipped to do the magic, and return a TextLine object that can be esily unpacked
into the underlying fields. Note that TextLine objects support the post-facto insertion
of new fields via the :meth:`TextLine.prepend() <baldaquin.serial_.TextLine.prepend()>`
and :meth:`TextLine.append() <baldaquin.serial_.TextLine.append()>` methods.


Module documentation
--------------------

.. automodule:: baldaquin.serial_
