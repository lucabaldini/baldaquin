:mod:`baldaquin.buf` --- Event buffering
========================================

The module provides a :class:`BufferBase <baldaquin.buf.BufferBase>` abstract
base class for data buffer, as well as a number of concrete classes:

* :class:`FIFO <baldaquin.buf.FIFO>`
* :class:`CircularBuffer <baldaquin.buf.CircularBuffer>`

The base class defines three basic primitives---``put_item()``, ``pop_item()`` and
``num_items()``, with obvious meanings, that need to be reimplemented in
concrete, derived classes. The implementation should be thread-safe, as a
buffer, by definition, will be accessed from multiple threads.

In addition, the base class provides a :meth:`flush() <baldaquin.buf.BufferBase.flush()>`
method that can dumps the current content of the buffer to file, assuming that
the path to the output file is properly set.

The basic semantic for the object is that one will have a thread calling
``buffer.put_item()`` any time there are data available, and another thread is
periodically calling ``flush()`` to get the data to disk.


Module documentation
--------------------

.. automodule:: baldaquin.buf
