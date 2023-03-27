:mod:`baldaquin.buf` --- Event buffering
========================================

The module provides a :class:`BufferBase <baldaquin.buf.BufferBase>` abstract
base class for data buffer, as well as a number of concrete classes, than
can be instantiated and used:

* :class:`FIFO <baldaquin.buf.FIFO>`
* :class:`CircularBuffer <baldaquin.buf.CircularBuffer>`

Buffer objects are collections of arbitrary items that support insertion and
removal in constant time. The base class defines four basic primitives:

* :meth:`put() <baldaquin.buf.BufferBase.put()>` to insert a single event into the
  buffer;
* :meth:`pop() <baldaquin.buf.BufferBase.pop()>` to retrieve (and remove) a single
  event from the buffer;
* :meth:`size() <baldaquin.buf.BufferBase.size()>` returning the number of events
  in the buffer at any given time;
* :meth:`clear() <baldaquin.buf.BufferBase.clear()>` to clear the buffer;

that need to be re-implemented in concrete, derived classes. The implementation should
be thread-safe, as a buffer might be accessed from multiple threads.

In addition, the base class provides a :meth:`flush() <baldaquin.buf.BufferBase.flush()>`
method that will write the current content of the buffer to file, assuming that
the path to the output file has been previously set via a
:meth:`set_output_file() <baldaquin.buf.BufferBase.set_output_file()>` call.

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
  exceeds the ``flush_interval`` value passed to the constructor.

By using the proper combination of ``flush_size`` and ``flush_interval`` it is
possible to achieve different effects, e.g., if ``flush_size`` is ``None``, then
the I/O will effectively happen at regular time intervals, according to the
``flush_interval`` value.


Module documentation
--------------------

.. automodule:: baldaquin.buf
