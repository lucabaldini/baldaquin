.. _xmaps:

XMAPS
=====

XMAPS is an array of 32 x 32 single-photon avalanche diodes (SPAD), for a total
of 1024 pixels with a built-in 7-bit counter. Additionally it features two peripheral
pixels for which we have access to the analog output.

The chip is divided in 8 logical buffer, each including 128 pixels, that are
readout in parallel. (That is, 128 pixels * 7 bits = 896 clock cycles are needed
for a full readout of the matrix.)

XMAPS comes with a 8-channels DAC to control the two peripheral pixels.
In the current implementation most of the channels of the DAC are actually
unused (i.e., disconnected), but it is good practice to set them to zero in
normal operation. The three used channels are:

* channel 4 (IBIAS): the bias current of the charge amplifier, in V. Note that
  3.3 V is off, and this should be the default value for operations not involving
  the peripheral analog pixels.
* channel 5 (IBR): the polarization voltage of the feedback network of the front-end.
  Defaults to 1.4 V.
* channel 7 (VTEST): the voltage level for the charge injection in the peripheral pixels.


API
---

.. automodule:: baldaquin.xmaps

.. automodule:: baldaquin.xmaps.protocol
