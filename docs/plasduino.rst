.. _plasduino:

plasduino
=========

`plasduino <https://pythonhosted.org/plasduino/>`_ is an old project that has
been running in the didactic labs at the University of Pisa since about 2013, and
is currently not maintained (nor maintainable)---if you are into vintage stuff,
you can glance through the original `repository <https://bitbucket.org/lbaldini/plasduino/src/main/>`_.

With our youthful exuberance, we thought we would do something awesome, and general,
and extensible---something that would go viral. (Sure...) Needless to say, the
project did not take off, although it served us well with the first-year Physics
students for more than ten years. But we are now taking this chance to resurrect
the project (or at least part of it) and adapt into this new framework.

plasduino is basically a collection of arduino sketches running onto an arduino
uno (with a small custom board plugged on top), along with a graphical user
interface to control the data acquisition.

The following rambling is essentially me reminding myself what we did years ago,
and why certain things are clumsy---at least for the limited part of the original
project we are trying to resurrect.


The communication protocol
--------------------------

The plasduino communication protocol is based on a few markers and operational codes
that are understood on both ends (the sketches running onto the arduino uno and the
client code on the computer controlling the data acquisition). All of these are
defined in the :mod:`baldaquin.plasduino.protocol` module.

In addition, there are two basic data structures that we use throughout:

* :class:`baldaquin.plasduino.protocol.AnalogReadout` encapsulates a simple analog
  readout, containing the information about the specific arduino analog input being
  latched, the timestamp (with ms resolution) of the readout and, obviously, the
  corresponding ADC value;
* :class:`baldaquin.plasduino.protocol.DigitalTransition` represents a digital
  transition that comes with its pin number, polarity (raising or falling edge)
  and timestamp (with us resolution).


The custom shields
------------------

We pretty much limit ourselves to the ``Lab1`` shield in use at the University of
Pisa. All the information is available
`here <https://bitbucket.org/lbaldini/plasduino/src/main/shields/lab1/lab1_v2/>`_.

For our purposes, anything that is relevant for interfacing to the shield from the
standpoint of the data acqisition is coded in the :mod:`baldaquin.plasduino.shields`
Python module.


The arduino sketches
--------------------

The code actually running on the arduino boards follows the typical arduino
structure, where there is an initial setup that is executed exactly once, followed
by an infinite loop.

.. warning::
  The fact that on the arduino side the configuration is one-shot is somewhat clashing
  with the baldaquin philosophy that system can be reconfigured before each start
  run. In other words, all the board configuration (e.g., pin assignment and
  sampling parameters) are hard-coded into each application and cannot be changed
  at runtime.

While all the original code is available on the old repository, we only copied over
the two relevant sketches, compiled for the arduino uno, in the new repo. They live
in:

* ``baldaquin/plasduino/sketches/digital_timer.hex`` (sketch number 1, version 3);
* ``baldaquin/plasduino/sketches/analog_sampling.hex`` (sketch number 2, version 3).


Loading the appropriate sketch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





Module documentation
--------------------

.. automodule:: baldaquin.plasduino.common

.. automodule:: baldaquin.plasduino.protocol

.. automodule:: baldaquin.plasduino.shields
