:mod:`baldaquin.buf` --- Event buffering
========================================

The module provides a :class:`BufferBase <baldaquin.buf.BufferBase>` abstract
base class for data buffer, as well as a number of concrete classes, i.e.:

* :class:`FIFO <baldaquin.buf.FIFO>`
* :class:`CircularBuffer <baldaquin.buf.CircularBuffer>`

Buffer objects are collections of arbitrary items that support insertion and
removal in constant time. The base class defines four basic primitives---``put()``,
``pop()``, ``size()`` and ``clear()``, with obvious meanings---that
need to be re-implemented in concrete, derived classes. The implementation should
be thread-safe, as a buffer, by definition, will be accessed from multiple threads.

In addition, the base class provides a :meth:`flush() <baldaquin.buf.BufferBase.flush()>`
method that can dump the current content of the buffer to file, assuming that
the path to the output file is properly set (via the constructor or the
dedicated :meth:`set_output_file() <baldaquin.buf.BufferBase.set_output_file()>`
method).

The basic semantic for the object is that one will have a thread calling
``buffer.put()`` any time there are data available, and another thread is
periodically calling ``buffer.flush()`` to get the data to disk.


Module documentation
--------------------

.. automodule:: baldaquin.buf
