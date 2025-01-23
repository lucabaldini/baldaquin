.. _release_notes:

Release notes
=============

* Major refactoring of the serial_ and arduino_ modules.
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
