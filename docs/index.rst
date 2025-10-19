.. baldaquin documentation master file, created by
   sphinx-quickstart on Sun Jul  3 11:54:55 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


==================================
baldaquin: BALd DAQ User INterface
==================================

.. figure:: _static/baldaquin_logo_light.png
   :width: 180pt
   :class: only-light
   :align: right

baldaquin (or the BALd DAQ User INterface) is an attempt at a general-purpose,
modular and reusable data acquisition framework based on modern technologies.
(And, before you get *too* excited, baldaquin is just a stub, and chances are
that it might never actually turn into something useful.)

By the way: :ref:`why baldaquin? <about>`

baldaquin strives at providing, in a simple fashion, the typical components
of an event-driven data acquisition system: a :ref:`run control <runctrl>`,
a logbook, extensive logging, :ref:`configuration <config>`,
:ref:`time-keeping <timeline>`, data-archival and test report
capabilities, as well as a slick graphical user interface, with the idea that
the user can then combine these capabilities and tailor them to their
application.


.. toctree::
   :caption: Overview
   :maxdepth: 2

   about
   install
   technologies

   release_notes
   api

   develop

.. toctree::
   :caption: Projects
   :maxdepth: 2

   plasduino