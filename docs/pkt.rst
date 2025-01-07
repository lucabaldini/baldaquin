.. _pkt:

:mod:`baldaquin.pkt` --- Binary packets
=======================================


This module contains all the facility to deal with binary packet data---by `packet`
we mean one piece one unit of binary data, and a packet can typically be imagined
as the elementary unit of information outputed by the hardware that is seen from
the DAQ side.

The :class:`BarePacketBase <baldaquin.pkt.BarePacketBase>` virtual class represents the
simplest, low-level interface to binary data. Subclasses should define the two
class variables

* ``FORMAT``, representing the packet layout, in a format that the Python
  `struct <https://docs.python.org/3/library/struct.html>`_ module understands; and
* ``SIZE``, representing the toal packet size in bytes.

Since in most situations each packet starts with a specific header, the module
provides a slightly more sophisticated virtual class, called
:class:`PacketBase <baldaquin.pkt.PacketBase>`, that adds some header machinery
on top of the fundamental layer. In this case, the ``HEADER`` class variable, in
addition to ``FORMAT`` and ``SIZE``


Mind that the ``FORMAT`` should match the type and the order of
the event fields fields. The format string is passed verbatim to the
Python ``struct`` module, and the related information is available at
https://docs.python.org/3/library/struct.html

The basic idea, here, is that the :meth:`pack() <baldaquin.event.PacketBase.pack()>`
method returns a bytes object that can be written into a binary file,
while the :meth:`unpack() <baldaquin.event.PacketBase.unpack()>` method does
the opposite, i.e., it constructs an event object from its binary representation
(the two are designed to round-trip). Additionally, the
:meth:`read_from_file() <baldaquin.event.PacketBase.read_from_file()>`
method reads and unpack one event from file.


Module documentation
--------------------

.. automodule:: baldaquin.pkt
