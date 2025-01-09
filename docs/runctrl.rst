.. _runctrl:

:mod:`baldaquin.runctrl` --- Run control
========================================

This module provides all the basic facilities to control the data acquisition at
an abstract level.


The finite-state machine
------------------------

The :class:`FiniteStateMachineLogic <baldaquin.runctrl.FiniteStateMachineLogic>` class
represents the basic logic of a finite-state machine (FSM) with four states, defined in
the :class:`FsmState <baldaquin.runctrl.FsmState>` enum class
(``RESET``, ``STOPPED``, ``RUNNING`` and ``PAUSED``).
This is an abstract class, and subclasses are ultimately responsible for
re-implementing all the virtual methods, i.e.,

* :meth:`setup() <baldaquin.runctrl.FiniteStateMachineBase.setup()>`,
  called in the ``RESET`` -> ``STOPPED`` transition;
* :meth:`teardown() <baldaquin.runctrl.FiniteStateMachineBase.teardown()>`,
  called in the ``STOPPED`` -> ``RESET`` transition;
* :meth:`start_run() <baldaquin.runctrl.FiniteStateMachineBase.start_run()>`,
  called in the ``STOPPED`` -> ``RUNNING`` transition;
* :meth:`stop_run() <baldaquin.runctrl.FiniteStateMachineBase.stop_run()>`,
  called in the ``RUNNING`` -> ``STOPPED`` transition;
* :meth:`pause() <baldaquin.runctrl.FiniteStateMachineBase.pause()>`,
  called in the ``RUNNING`` -> ``PAUSED`` transition;
* :meth:`resume() <baldaquin.runctrl.FiniteStateMachineBase.resume()>`,
  called in the ``PAUSED`` -> ``RUNNING`` transition;
* :meth:`stop() <baldaquin.runctrl.FiniteStateMachineBase.stop()>`,
  called in the ``PAUSED`` -> ``STOPPED`` transition.


.. figure:: figures/baldaquin_fsm.png


These virtual methods are actually never called directly, and all the interactions
with concrete instances of subclasses typically happen through four methods, mapping
to the typical buttons of a transport bar, that call the proper hook to set the FSM
in a given state, depending on the current state:

* :meth:`set_reset() <baldaquin.runctrl.FiniteStateMachineBase.set_reset()>`;
* :meth:`set_stopped() <baldaquin.runctrl.FiniteStateMachineBase.set_stopped()>`;
* :meth:`set_running() <baldaquin.runctrl.FiniteStateMachineBase.set_running()>`;
* :meth:`set_paused() <baldaquin.runctrl.FiniteStateMachineBase.set_paused()>`.

This assume that the target state can be reached via a valid transition from the
current state, and if that is not the case, an
:class:`InvalidFsmTransitionError <baldaquin.runctrl.InvalidFsmTransitionError>`
error is raised.


The :class:`FiniteStateMachineBase <baldaquin.runctrl.FiniteStateMachineBase>` class
is a subclass of :class:`FiniteStateMachineLogic <baldaquin.runctrl.FiniteStateMachineLogic>`
that, in addition to all the functionality of the base class, emits a
``state_changed`` (:class:`FsmState <baldaquin.runctrl.FsmState>`)
signal whenever the underlying state changes, signaling the state `after` the transition.
This is still an abstract class, and subclasses are ultimately responsible for
re-implementing all the relevant virtual methods.


The run control
---------------

The :class:`RunControlBase <baldaquin.runctrl.RunControlBase>` class is a
subclass of :class:`FiniteStateMachineBase <baldaquin.runctrl.FiniteStateMachineBase>`
and, on top of the base class, is adding all the logic for controlling the data
acquisition, including:

* the (coarse, that is, at the wall clock level) time keeping;
* the I/O, including the management and location of configuration files, log files,
  and actual data files;
* the book-keeping of the basic run statistics, and its synchronization with the
  control GUI, when relevant;
* the execution of custom user applications, which is where the actual semantic
  of the data acquisition is implemented.

.. seealso:: :ref:`timeline`, :ref:`app`.

:class:`RunControlBase <baldaquin.runctrl.RunControlBase>` is still an abstract
class that cannot be instantiated directly. Subclasses must, at the very minimum,
define the ``_PROJECT_NAME`` class attribute, and a minimal working example of a
concrete run control will look like:

.. code::

   class MyRunControl:

      _PROJECT_NAME = 'my_project'

Any run control object is equipped to emit the following signals:

* ``run_id_changed`` (int ``run_id``) is emitted whenever the run ID is `changed`,
  that is, at the beginning of each run;
* ``user_application_loaded`` (:class:`UserApplicationBase <baldaquin.app.UserApplicationBase>` ``user_app``)
  is emitted whenever a user application is loaded (and the full application
  object is passed along with the signal);
* ``uptime_updated`` (float ``uptime``) is emitted whenever the uptime for the
  run control is updated;
* ``event_handler_stats_updated`` (int ``num_packets_processed``, int ``num_packets_written``,
  int ``num_bytes_written``, float ``average_event_rate``) is emitted whenever
  the event handler provides updates for the underlying statistics.

.. seealso:: :ref:`event`.



Basics: test-stand and run ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the very basic levels there are two quantities that are central to the state
of the run control at any given time:

* the test-stand ID is an integer number identifying the test equipment being
  used for the data taking;
* the run ID is another integer number uniquely identifying a given portion
  of data taking, done for a specific purpose, through which the test configuration
  stays rigorously unchanged.

The test-stand ID and the run ID are read from the proper configuration files
when the run control is instantiated, and the run ID is incremented by one unit
each time the run control is started---this is really all that there is to know.

.. warning::

   Default configuration files for both the test-stand and the run ID will be
   automatically created for you when a run control is instantiated if they
   don't exist. While this is likely what you want for the run ID, the responsibility
   of keeping track of the test-stand ID is entirely on you, and you will want
   to edit the file by hand as needed.



I/O and file locations
~~~~~~~~~~~~~~~~~~~~~~

The basic rules for the location of the files managed by the run control are
determined by the ``_PROJECT_NAME`` class attribute, and they boil down to:

* configuration files (e.g., ``test_stand.cfg`` and ``run.cfg``) live in
  ``$HOME/.baldaquin/_PROJECT_NAME``;
* all run-specific data products (that is, data files and log files) are saved
  in ``$BALDAQUIN_DATA/_PROJECT_NAME`` if the ``$BALDAQUIN_DATA`` environmental
  variable is defined, and in ``$HOME/baldaquindata/_PROJECT_NAME`` otherwise---more
  specifically, a self-contained folder named after the test-stand and run ID is
  created there every time a run is started;
* user applications provide their own semantics to control the location of the
  relevant configuration files, but the latter are typically located in
  ``$HOME/.baldaquin/_PROJECT_NAME/apps``.



Loading a user application
~~~~~~~~~~~~~~~~~~~~~~~~~~

Although in real life the run control will typically be controlled by a
graphical user interface, the basic semantic for starting a data acquisition
programmatically, with a given run control and user application, reads:

.. code::

   run_control = MyRunControl()
   user_app = MyUserApplication()
   run_control.load_user_application(user_application)
   run_control.set_running()

.. seealso:: :ref:`gui`, :ref:`app`.

Note that the run control will emit an :class:`AppNotLoadedError <baldaquin.runctrl.AppNotLoadedError>`
exception upon any attempt to change the underlying state of the FSM without
an actual user application being properly loaded.


Module documentation
--------------------

.. automodule:: baldaquin.runctrl
