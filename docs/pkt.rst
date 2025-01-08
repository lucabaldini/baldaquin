.. _pkt:

:mod:`baldaquin.pkt` --- Binary packets
=======================================


This module contains all the facilities to deal with binary packet data---by `packet`
we mean one piece one unit of binary data, and a packet can typically be imagined
as the elementary unit of information outputted by the hardware that is seen from
the DAQ side, containing one (in the simplest case) or more events.

The module provides the :class:`AbstractPacket <baldaquin.pkt.AbstractPacket>`
abstract class as a base for all the packet classes. Subclass should implement
the following interfaces

* a ``payload`` property, returning the underlying binary buffer (typically a ``bytes``
  object);
* a ``fields`` property, i.e., a tuple of string with the names of all the fields
  that have to be extracted from the payload when a class instance is unpacked;
* the ``__len__()`` dunder method, returning the size of the payload in bytes;
* the ``__iter__()`` dunder method, that makes the class iterable;
* a ``pack()`` method, packing all the fields into the corresponding payload;
* an ``unpack()`` method, unpacking the payload into the corresponding fields, with
  the understanding that ``pack()`` and ``unpack()`` should be guardanteed to roundtrip.

From a DAQ standpoint, the main use of concrete packet classes should be something
along the lines of

>>> packet = Packet.unpack(data)

That is: you have a piece of binary data from the hardware, you know the layout
of the packet, you can unpack it in the form a useful data structure that is easy
to work with, plot, write to file, and alike.

Being able to go the other way around (i.e., initialize a packet from its fields)
is useful from a testing standpoint, and that is the very reason for provinding the
``pack()`` interface, that does things in this direction.

.. warning::
  We have not put much thought, yet, into support for variable-size packets, and
  the interfaces might change as we actually implement and use them. At this time
  the user should feel comfortable in using the
  :class:`FixedSizePacketBasePacket <baldaquin.pkt.FixedSizePacketBase>` base
  class and the associated :meth:`packetclass <baldaquin.pkt.packetclass>`
  decorator.


Fixed-size packets
------------------

In its simplest incarnation, a packet is just a simple set of number packed in binary
format with a well-defined layout and with a fixed size. This module provides the
:meth:`packetclass <baldaquin.pkt.packetclass>` decorator and the
:class:`FixedSizePacketBasePacket <baldaquin.pkt.FixedSizePacketBase>` base class
to define concrete fixed-size packet structures.

The :meth:`packetclass <baldaquin.pkt.packetclass>` decorator is loosely related
to the Python ``dataclass`` decorator, and what it does is essentially providing
a class constructor based on class annotations. The basic contract is that for any
annotation in the form of

>>> field_name: format_char

a new attribute with the given ``field_name`` is added to the class, with the
``format_char`` specifying the type of the field in the packet layout, according
to the rules in the Python `struct <https://docs.python.org/3/library/struct.html>`_
module, e.g.,

* ``b`` and ``B``: signed/unsigned char (1-byte standard size), mapping to a Python integer;
* ``h`` and ``H``: signed/unsigned short int (2-byte standard size), mapping to a Python integer;
* ``i`` and ``I``: signed/unsigned int (4-byte standard size), mapping to a Python integer;
* ``l`` and ``L``: signed/unsigned long int (4-byte standard size), mapping to a Python integer;
* ``q`` and ``Q``: signed/unsigned long long int (8-byte standard size), mapping to a Python integer;
* ``f``: single-precision floating point number, mapping to a Python float;
* ``d``: double-precision floating point number, mapping to a Python float.

If the format charater is not supported, a
:class:`FormatCharacterError <baldaquin.pkt.FormatCharacterError>` exception is
raised.

Additionally, if a value is provided to the class annotation

>>> field_name: format_char = value

the value of the corresponding attribute is checked at runtime, and a
:class:`FieldMismatchError <baldaquin.pkt.FieldMismatchError>` exception is
raised if the two do not match. (This is useful, e.g., when a packet has a fixed
header that need to be checked within the event loop.)

Finally, a ``layout`` class attribute can be optionally specified to control the
byte order, size and alignment of the packet, again following the very same conventions
of the Python `struct <https://docs.python.org/3/library/struct.html>`_
module, i.e.,

* ``@``: native byte order, size and alignment;
* ``=``: native byte order, standard size;
* ``<``: little-endian, standard size;
* ``>``: big-endian, standard size;
* ``!``: network (= big-endian), standard size.

If no layout is specified, ``@`` is assumed. If the layout character is not supported
a :class:`LayoutCharacterError <baldaquin.pkt.LayoutCharacterError>` exception is
raised.

The :class:`FixedSizePacketBasePacket <baldaquin.pkt.FixedSizePacketBase>` base class
complement the decorator and implements the protocol defined by the
:class:`AbstractPacket <baldaquin.pkt.AbstractPacket>` abstract class. For instance,
the following snippet

.. code-block::

    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = '>'

        header: 'B' = 0xff
        pin_number: 'B'
        timestamp: 'Q'

defines a fully fledged packet class with three fields (big endian, standard size)
that can be used as advertised

>>> packet = Trigger(0xff, 1, 15426782)
>>> print(packet)
>>> Trigger(header=255, pin_number=1, timestamp=15426782, payload=b'\xff\x01\x00\x00\x00\x00\x00\xebd\xde', _format=>BBQ)
>>> print(len(packet))
>>> 10
>>> print(isinstance(packet, AbstractPacket))
>>> True

(you will notice that when you create a packet from the constructor, the binary
representation is automatically calculated using the ``pack()`` interface).

And, of course, in real life (as opposed to unit-testing) you will almost always
find yourself unpacking things, i.e.,

>>> packet = Trigger.unpack(b'\xff\x01\x00\x00\x00\x00\x00\xebd\xde')
>>> print(packet)
>>> Trigger(header=255, pin_number=1, timestamp=15426782, payload=b'\xff\x01\x00\x00\x00\x00\x00\xebd\xde', _format=>BBQ)

(i.e., you have binary data from your hardware, and you can seamlessly turned into
a useful data structure that you can interact with.)

Packet objects defined in this way are as frozen as Python allows---you can't modify
the values of the basic underlying fields once an instance has been created

>>> packet.pin_number = 0
>>> AttributeError: Cannot modify Trigger.pin_number'

and this is done with the goal of preserving the correspondence between the binary
paylod and the unpacked field values at runtime.

You can define new fields, though, and the ``AbstractPacket`` protocol, just as
plain Python ``dataclasses``, provides a ``__post_init__()`` hook which is called
at the end of the constructor (and is doing nothing by default). This is useful,
e.g., for converting digitized values into the corresponding physical values.
Say, for instance, that the ``timestamp`` in our simple ``Trigger`` class is the
the number of microseconds since the last reset latched with an onboard counter, and
we want to convert them to seconds. This can be achieved by something along the
lines of

.. code-block::

    @packetclass
    class Trigger(FixedSizePacketBase):

        layout = '>'

        header: 'B' = 0xff
        pin_number: 'B'
        microseconds: 'Q'

        def __post_init__(self):
            self.seconds = self.microseconds / 1000000

with the understanding that

>>> packet = Trigger(0xff, 1, 15426782)
>>> print(packet.seconds)
>>> 15.426782






Module documentation
--------------------

.. automodule:: baldaquin.pkt
