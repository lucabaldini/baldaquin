.. _event:

:mod:`baldaquin.event` --- Event handler
========================================

The module provides the necessary facilities for asynchronous event handling.
:class:`EventHandlerBase <baldaquin.event.EventHandlerBase>` is an abstract
base class for runnable tasks that can be overloaded to create concrete
event handler to be used within the run control.

.. code-block::

   evt_handler = MyEventHandler(*args, **kwargs) # Note you need a concrete class, here.
   pool = QtCore.QThreadPool.globalInstance()
   pool.start(evt_handler)

   # A concurrent thread can flush the data buffer to disk asynchronously...

   evt_handler.stop()
   pool.waitForDone()
   evt_handler.buffer.flush()

In the dedault implementation the
:meth:`run() <baldaquin.event.EventHandlerBase.run()>`
method is simply calling
:meth:`process_event() <baldaquin.event.EventHandlerBase.process_event()>`
repeatedly (on a separate thread) and putting in the data buffer whatever
the latter returns, under the condition that the event handler is runnging.

Subclasses will overload
:meth:`process_event() <baldaquin.event.EventHandlerBase.process_event()>`
to achieve the desired behavior.
You can look at :class:`MockEventHandler <baldaquin.event.MockEventHandler>` for a
concrete example.


Module documentation
--------------------

.. automodule:: baldaquin.event
