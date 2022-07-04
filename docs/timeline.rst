.. _timeline:

:mod:`baldaquin.timeline` --- Time keeping
==========================================

The module provides the two basic data structures used by baldaquin to keep track
of the time on the computer hosting the data acquisition: the
:class:`Timeline <baldaquin.timeline.Timeline>` and
:class:`Timestamp <baldaquin.timeline.Timestamp>` objects.

A timeline is a simple object that keeps track of the date, time and the number
of seconds elapsed since a fixed origin defined at creation time. It exposes
a single public method :meth:`Timeline.latch() <baldaquin.timeline.Timeline.latch()>`
that reads the system time at a given moment and returns the corresponding
:class:`Timestamp <baldaquin.timeline.Timestamp>` object.

In order to avoid the pitfalls connected with using the local time
(and the documentation of the `pyzt <https://pythonhosted.org/pytz/>`_ package
is a very entertaining reading in this respect), Timeline objects work internally
in the UTC time zone, and the ``seconds`` field of a Timestamp object is *always*
to be intended in UTC. That said, we recognize that the local time is often the
most interesting piece of information when it comes to understanding when something
happened in a *specific place*, and to this end Timestamp objects keep track
internally of the local time, too. It's just that local time isn't that great to
reconstruct an a absolute position in time unless one keeps track of a series of
other things, such as the time zone and the daylight saving flag.

baldaquin tries and strike a sensible compromise between generality and simplicity,
the basic usage ot the timeline objects being:

>>> from baldaquin.timeline import Timeline
>>>
>>> t = Timeline()
>>> timeline = Timeline()
>>> t1 = timeline.latch()
>>> print(t1)
2022-07-04 16:44:18.915834+02:00 (1656945858.915834 s)
>>> print(t1.utc_datetime)
2022-07-04 14:44:18.915834+00:00
>>> print(t1.local_datetime)
2022-07-04 16:44:18.915834+02:00
>>> print(t1.seconds)
1656945858.915834
>>> t2 = timeline.latch()
>>> t2 - t1
57.82228899002075

By default the Timeline origin is set to January 1, 1970 at 00:00:00 (UTC), in
such a way that the ``seconds`` field of a Timestamp objects coincides with the
familiar POSIX time. Setting the origin to a different value allow, e.g., to
emulate the mission elapsed time (MET) concept that is common in space missions.

.. warning::

   It is probably worth mentioning that all
   :meth:`Timeline.latch() <baldaquin.timeline.Timeline.latch()>` really does
   internally is the simple call

   .. code-block:: python

      utc_datetime = datetime.datetime.now(datetime.timezone.utc)

   and therefore one should not really expect the results to be accurate to
   6 significant digits---results may vary depending of the OS and the
   configuration of the host computer. Nonetheless, the module should be more
   than adequate for book-keeping purposes.


Module documentation
--------------------

.. automodule:: baldaquin.timeline
