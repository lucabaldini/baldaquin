.. _widgets:

:mod:`baldaquin.widgets` --- Advanced widgets
=============================================

This modules provides all the advanced widgets that baldaquin provides to
assemble complex user interfaces. Among a few other things, the module includes
the following generic classes:

* :class:`CardWidget <baldaquin.widgets.CardWidget>`: a read-only widget
  that is meant to display an arbitrary series of (key, value) pairs
  arranged vertically;
* :class:`ConfigurationWidget <baldaquin.widgets.ConfigurationWidget>`: a
  read/write interface to concrete subclasses of the
  :class:`ConfigurationBase <baldaquin.config.ConfigurationBase>` class that
  allow to display and edit configuration objects;
* :class:`LoggerDisplay <baldaquin.widgets.LoggerDisplay>`: a ``QTextEdit`` subclass
  acting as a graphical sink to the application-wide logger (based on the
  `loguru <https://loguru.readthedocs.io/en/stable/>`_ library);
* :class:`ControlBar <baldaquin.widgets.ControlBar>`: a horizontal array of
  ``QPushButton`` objects that allow to interact with the main
  :class:`RunControl <baldaquin.runctrl.RunControl>` instance.

In addition, the module provides a number of specialized, ready-to-use
subclasses of these generic classes, that can be assembled within complex
user interfaces:

* :class:`RunControlCard <baldaquin.widgets.RunControlCard>`: a specialized card
  widget designed to show the status of the :class:`RunControl <baldaquin.runctrl.RunControl>`.


Module documentation
--------------------

.. automodule:: baldaquin.widgets
