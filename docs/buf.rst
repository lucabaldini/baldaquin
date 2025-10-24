:mod:`~baldaquin.buf` --- Event buffering
=========================================

The module provides all the necessary facilities to buffer the binary data coming
from the hardware and make sure they get written to disk in the intended way.


Buffers
-------

The class hierarchy within the module rotates around the
:class:`AbstractBuffer <baldaquin.buf.AbstractBuffer>` abstract class, representing
a collection of packets that supports insertion and removal in constant time.
This abstract class requires the following interfaces to be defined:

* :meth:`_do_put() <baldaquin.buf.BufferBase._do_put()>` to insert a single packet
  into the buffer (the actual hook to instert packets is actually called
  :meth:`put() <baldaquin.buf.BufferBase.put()>`, but this is implemented in the abstract
  class so that we can consistently enforce that the packets being inserted into
  the buffer are of the proper type, and subclasses implement the specific semantic
  of the method in :meth:`_do_put() <baldaquin.buf.BufferBase._do_put()>`);
* :meth:`pop() <baldaquin.buf.BufferBase.pop()>` to retrieve (and remove) a single
  packet from the buffer;
* :meth:`size() <baldaquin.buf.BufferBase.size()>` returning the number of events
  in the buffer at any given time;
* :meth:`clear() <baldaquin.buf.BufferBase.clear()>` to clear the buffer;

The module then provides two concrete sub-classes, acting as FIFOs, than can be
used in practice:

* :class:`FIFO <baldaquin.buf.FIFO>`
* :class:`CircularBuffer <baldaquin.buf.CircularBuffer>`

Both concrete classes are thread-safe, as a buffer is in general accessed by
multiple threads. The basic usage looks like

>>> buffer = FIFO()
>>> print(buffer.size())
>>> 0
>>> buffer.put(packet)
>>> print(buffer.size())
>>> 1
>>> packet = buffer.pop()
>>> print(buffer.size())
>>> 0

In addition, the base class provides a :meth:`flush() <baldaquin.buf.BufferBase.flush()>`
method that will write the entire buffer content to file (more of the internals
of this mechanism in the next section).

The concrete buffer classes make no attempt at synchronizing the I/O, but they
do provide useful hooks for external code to figure out whether a
:meth:`flush() <baldaquin.buf.BufferBase.flush()>` operation is needed.
More specifically:

* :meth:`almost_full() <baldaquin.buf.BufferBase.almost_full()>` returns ``True``
  when the number of events in the buffer exceeds the ``flush_size`` value passed
  to the constructor;
* :meth:`time_since_last_flush() <baldaquin.buf.BufferBase.time_since_last_flush()>`
  returns the time (in seconds) elapsed since the last
  :meth:`flush() <baldaquin.buf.BufferBase.flush()>` call;
* :meth:`flush_needed() <baldaquin.buf.BufferBase.flush_needed()>` returns ``True``
  when either the buffer is almost full or the time since the last flush
  exceeds the ``flush_timeout`` value passed to the constructor.

By using the proper combination of ``flush_size`` and ``flush_timeout`` it is
possible to achieve different effects, e.g., if ``flush_size`` is ``None``, then
the I/O will effectively happen at regular time intervals, according to the
``flush_timeout`` value.


Sinks
-----

The operation of writing the buffer to file(s) is handled through the
:class:`Sink <baldaquin.buf.Sink>` concept. A sink is a descriptor than can be
attached to a buffer, and encapsulates all the information that is necessary
to write the packets out in a suitable format.

In order to be able to be flushed, a buffer must have at least a primary sink
attached to it, which by defaults writes the packets `verbatim` to the output file
in binary form.

>>> buffer = CircularBuffer()
>>> buffer.set_primary_sink(file_path)
>>> ...
>>> buffer.flush() # <- This will write to disk the packets in the buffer.

In addition, custom sinks can be added to a buffer, specifying the path to the
output file, the write mode, the packet formatter and an optional header. By using
the proper combination of sinks, one can achieve useful things, such as writing the
data out in binary format and, at the same time, write a text file where the
packets are formatted with a suitable ASCII representation, i.e.,

>>> buffer = CircularBuffer()
>>> buffer.set_primary_sink(binary_file_path)
>>>
>>> # Define a custom sink---the packet class should have a ``as_text()`` hook
>>> # returning a suitable text representation of the thing
>>> buffer.add_custom_sink(text_file_path, WriteMode.TEXT, Packet.as_text, header)
>>>
>>> # ... fill the buffer with some packets.
>>>
>>> buffer.flush() # <- This will write two output files!


Module documentation
--------------------

.. automodule:: baldaquin.buf
