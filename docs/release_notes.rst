.. _release_notes:

Release notes
=============


Version 0.8.2 (2025-10-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Small fix for the package logo on PyPI.
* Pull requests merged and issues closed:

    - https://github.com/lucabaldini/baldaquin/pull/79
    - https://github.com/lucabaldini/baldaquin/issues/78


Version 0.8.1 (2025-10-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Package automatically built and published to PyPI on git tag push.
* Pull requests merged and issues closed:

    - https://github.com/lucabaldini/baldaquin/pull/77
    - https://github.com/lucabaldini/baldaquin/issues/75


Version 0.8.0 (2025-10-21)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Migrate histogram and strip chart functionality from internal baldaquin modules
  to the external aptapy library.
* New silly_strip example application added to demonstrate the strip chart functionality.
* Pull requests merged and issues closed:

    - https://github.com/lucabaldini/baldaquin/pull/74
    - https://github.com/lucabaldini/baldaquin/issues/70


Version 0.7.0 (2025-10-19)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adopted src/ layout with baldaquin package moved to src/baldaquin/
* Introduced dynamic versioning with git integration
* Replaced Makefile with nox sessions for development tasks
* Updated all copyright headers to 2025
* Consolidated environment/logging setup into dedicated modules
* Default quote character changes from single to double quote.
* Major clean up and linting.
* Pull requests merged and issues closed:

    - https://github.com/lucabaldini/baldaquin/pull/73
    - https://github.com/lucabaldini/baldaquin/issues/69


*baldaquin 0.6.0 (Wed, 28 May 2025 11:03:01 +0200)*

* Major restructuring of the configuration facilities, which are now multi-section.
* Logging and buffering configuration controlled from the main window.
* Configuration update from file now resilient to format changes.
* Fix for some funky behavior of the ParameterSpinBox class.
* Minor refactoring of the buffer classes, which are now always unbounded.
* Minor plasduino cleanup.
* New TextLine class and associated text serial communication protocol.
* New compilation and upload scheme for the arduino sketeches and associated artifacts.
* Major refactoring of the xnucleo monitoring, and auto-upload functionality implemented.
* Port class renamed as PortInfo.
* New ArduinoSerialInterface and ArduinoEventHandler classes.
* Cleanup, docs and unit tests added.
* Signature of SerialInterface.connect() changed to accept a PortInfo object.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/61
      * https://github.com/lucabaldini/baldaquin/pull/62
      * https://github.com/lucabaldini/baldaquin/pull/66
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/54
      * https://github.com/lucabaldini/baldaquin/issues/56
      * https://github.com/lucabaldini/baldaquin/issues/57
      * https://github.com/lucabaldini/baldaquin/issues/64
      * https://github.com/lucabaldini/baldaquin/issues/64


*baldaquin 0.5.0 (Mon, 19 May 2025 09:29:50 +0200)*

* Some bugs and rough edges in the plasduino extension have been fixed.
* New generic monitoring application based on arduino + x-nucleo board.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/53
      * https://github.com/lucabaldini/baldaquin/pull/59
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/50
      * https://github.com/lucabaldini/baldaquin/issues/51


*baldaquin 0.4.0 (Fri, 31 Jan 2025 15:53:59 +0100)*

* Development notes added to the documentation.
* Setup files for Windows added.
* Link to the output folder added in the main GUI.
* Serialization/deserialization methods implemented for Timestamp and PacketStatistics
  objects.
* RunReport class added.
* RunControl now saving the run report and the configuration in the output folder.
* Merging pull requests
      * https://github.com/lucabaldini/baldaquin/pull/49
      * https://github.com/lucabaldini/baldaquin/pull/48
      * https://github.com/lucabaldini/baldaquin/pull/47
* Issue(s) closed
      * https://github.com/lucabaldini/baldaquin/issues/45
      * https://github.com/lucabaldini/baldaquin/issues/44
      * https://github.com/lucabaldini/baldaquin/issues/29
      * https://github.com/lucabaldini/baldaquin/issues/19


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