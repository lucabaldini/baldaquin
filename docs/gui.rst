.. _gui:

:mod:`~baldaquin.gui` --- Basic GUI elements
============================================

This module provides all the basic building blocks for the advanced GUI
widgets.


Low-level widgets
-----------------

At the lowest level, the module provides a number of classes that act as lightweight
wrappers over standard Qt widget, with the twofold purpose of enforcing consistency
in the overall look and feel of the interface and minimizing boilerplate code:

* :class:`Button <baldaquin.gui.Button>` represents a simple button equipped with
  an icon, and is used in the :class:`ControlBar <baldaquin.gui.ControlBar>`;
* :class:`DataWidgetBase <baldaquin.gui.DataWidgetBase>` is the basic (abstract)
  building block for mapping key-value pairs: it is nothing more than a pair of
  widget---a ``QLabel`` holding a title and a generic widget holding some data---arranged
  in a vertical layout.


Displaying data
---------------

The :class:`DisplayWidget <baldaquin.gui.DisplayWidget>` is the simplest
:class:`DataWidgetBase <baldaquin.gui.DataWidgetBase>` subclass, and also the
basic building block for displaying data in a read-only fashion. The specific
widget holding the value is a ``QLabel``.

:class:`DisplayWidget <baldaquin.gui.DisplayWidget>` object are seldom instantiated
directly, and their most common incarnation, by far, is the
:class:`CardWidget <baldaquin.gui.CardWidget>`, inspired to the material design
guidelines at https://material.io/components/cards.
Cards are surfaces that display content and actions on a single topic and, for
our purposes, cards are basically ``QFrame`` objects holding a vertical layout
to which we attach :class:`DisplayWidget <baldaquin.gui.DisplayWidget>`
instances. Cards are typically driven by ``Enum`` objects, along the lines of

.. code:: python

  class MyCardField(Enum):

      EGGS = 'Eggs'
      SPAM = 'Spam'

  class MyCard(CardWidget):

      _FIELD_ENUM = MyCardField


Among the specific sub-classes that the module provides (and that can be a good
source of inspiration as to what is the level of flexibility of this approach) are:

* :class:`RunControlCard <baldaquin.gui.RunControlCard>`;
* :class:`EventHandlerCard <baldaquin.gui.EventHandlerCard>`.

.. seealso:: :ref:`runctrl`, :ref:`event`.


Displaying configurations
-------------------------

The module provides a series of custom widgets for the purpose of displaying
configuration parameters, designed to interact natively with instances of the
:class:`ConfigurationBase <baldaquin.config.ConfigurationBase>` abstract class:

* :class:`ParameterCheckBox <baldaquin.gui.ParameterCheckBox>`,
  mapping to ``bool`` parameters;
* :class:`ParameterSpinBox <baldaquin.gui.ParameterSpinBox>`,
  mapping to ``int`` parameters;
* :class:`ParameterDoubleSpinBox <baldaquin.gui.ParameterDoubleSpinBox>`,
  mapping to ``float`` parameters;
* :class:`ParameterLineEdit <baldaquin.gui.ParameterLineEdit>`,
  mapping to ``str`` parameters with no ``choices`` constraints;
* :class:`ParameterComboBox <baldaquin.gui.ParameterComboBox>`,
  mapping to ``str`` parameters with ``choices`` constraints.

These widgets, too, are seldom instantiated directly, and live more commonly
within :class:`ConfigurationWidget <baldaquin.gui.ConfigurationWidget>` objects,
where they are dinamically mapped to the proper parameter types within a given
configuration object.

.. seealso:: :ref:`config`.


Embedding matplotlib
--------------------

The :class:`PlotCanvasWidget <baldaquin.gui.PlotCanvasWidget>` is the main
resource to embed a matplotlib figure, along the lines of the documentation at
https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html.

This specific widget is equipped with a ``QTimer`` object that can be used
to manage the updating of the underlying plot within an event loop.


The control bar
---------------

The :class:`ControlBar <baldaquin.gui.ControlBar>` is deigned to manage the
run control from a GUI environment and implements the same exact semantics of the
finite-state machine upon which the latter is based. It emits four different
signals

* ``set_reset_triggered`` ()
* ``set_stopped_triggered`` ()
* ``set_running_triggered`` ()
* ``set_paused_triggered`` ()

and each one is connected at runtime to the proper change of state in the run control.



The main window
---------------





Module documentation
--------------------

.. automodule:: baldaquin.gui
