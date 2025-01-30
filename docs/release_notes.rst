.. _release_notes:

Release notes
=============


* Link to the otuput folder added in the main GUI.
* Serialization/deserialization methods implemented for Timestamp and PacketStatistics
  objects.
* RunReport class added.
* RunControl now saving the run report and the configuration in the output folder.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/48
      * https://github.com/lucabaldini/baldaquin/pull/47
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/45
      * https://github.com/lucabaldini/baldaquin/issues/44
      * https://github.com/lucabaldini/baldaquin/issues/29


*baldaquin 0.3.1 (Wed, 29 Jan 2025 06:13:22 +0100)*

* RunControl properly reset when the window is closed.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/43
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/28


*baldaquin 0.3.0 (Tue, 28 Jan 2025 15:09:37 +0100)*

* baldaquin main command-line interface revamped, and rudimentary application
  launcher added.
* ``pyproject.toml`` file updated to ship the baldaquin cli.
* ``requirements.txt`` removed, as it was redundant with ``pyproject.toml``.
* New ``main()`` entry point added to all the applications.
* Installation notes added to the documentation, and a few other minor tweaks.
* IntEnum used where appropriate.
* Three basic plasduino apps fully operational.
* Inheritance supported in the ``@packetclass`` decorator.
* ``payload`` class member renamed as ``data`` in the ``AbstractPacket`` class.
* Major restructuring of the packet text formatting facilities.
* New ``PacketFile`` class added to support packet text output.
* ``pre_start()`` and ``post_stop`` hooks added to the ``UserApplicationBase``
  class.
* Docs updated and unit tests added.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/41
      * https://github.com/lucabaldini/baldaquin/pull/39
      * https://github.com/lucabaldini/baldaquin/pull/36
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/38
      * https://github.com/lucabaldini/baldaquin/issues/34
      * https://github.com/lucabaldini/baldaquin/issues/20
      * https://github.com/lucabaldini/baldaquin/issues/12
      * https://github.com/lucabaldini/baldaquin/issues/10


*baldaquin 0.2.1 (Thu, 23 Jan 2025 15:57:29 +0100)*

* Release manager now updating the pyproject.toml file.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/33
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/32


*baldaquin 0.2.0 (Thu, 23 Jan 2025 14:17:00 +0100)*

* Major refactoring of the ``serial_`` and ``arduino_`` modules.
* New, experimental, baldaquin command-line utility added.
* Sketch auto-upload implemented in plasduino.
* Sketch compilation capability added.
* BALDAQUIN_SCRATCH folder added.
* New ``pre_start()`` hook added to the ``UserApplicationBase`` class.
* Added specific hooks for text sinks in the ``AbstractPacket`` class, and default
  implementation provided in ``FixedSizePacketBase``.
* Documentation expanded and revised.
* Unit tests added.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/27
      * https://github.com/lucabaldini/baldaquin/pull/30
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/25


*baldaquin 0.1.3 (Wed, 15 Jan 2025 08:59:44 +0100)*

* Major refactoring of the buf.py module.
* Buffer sinks added to add flexibility to the generation of output files.
* Default character encoding now defined in baldaquin.__init__
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/21
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/13


*baldaquin 0.1.2 (Sat, 11 Jan 2025 10:52:28 +0100)*

* Fix a bunch of pylint warnings
* Code of conduct added.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/14
      * https://github.com/lucabaldini/baldaquin/pull/15
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/9


*baldaquin 0.1.1 (Sat, 11 Jan 2025 02:09:53 +0100)*

* Small fix in the documentation compilation.


*baldaquin 0.1.0 (Sat, 11 Jan 2025 02:03:41 +0100)*

Initial stub
