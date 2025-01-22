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
>>> [DEBUG] Port(name='/dev/ttyS0', device_id=(vid=None, pid=None), manufacturer=None)
>>> [DEBUG] Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [INFO] Done, 2 device(s) found.

The method allows to filter over device IDs (or, equivalently, over vid, pid tuples)
which comes handy when one is interested in a particular device or set of devices.

>>> ports = serial_.list_com_ports((0x2341, 0x0043))
>>> [INFO] Scanning serial devices...
>>> [DEBUG] Port(name='/dev/ttyS0', device_id=(vid=None, pid=None), manufacturer=None)
>>> [DEBUG] Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')
>>> [INFO] Done, 2 device(s) found.
>>> [INFO] Filtering port list for specific devices: [(vid=0x2341, pid=0x43)]...
>>> [INFO] Done, 1 device(s) remaining.
>>> [DEBUG] Port(name='/dev/ttyACM0', device_id=(vid=0x2341, pid=0x43), manufacturer='Arduino (www.arduino.cc)')


In addition, the :class:`SerialInterface <baldaquin.serial_.SerialInterface>` 
acts like a base class that can be subclassed to implement any specific 
communication protocol over the serial port.


Module documentation
--------------------

.. automodule:: baldaquin.serial_
