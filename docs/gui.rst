.. _gui:

:mod:`baldaquin.gui` --- Basic GUI elements
===========================================

This module provides all the basic building blocks for the advanced GUI
widgets.

Particularly, the module define a generic :class:`DisplayWidget <baldaquin.gui.DisplayWidget>`
to display a single piece of information in the form of a (label, value) pair,
which is useful to build slick card-time widgets, along with a series of
specific input widgets, for different data types, designed to interact natively
with instances of the :class:`ConfigurationBase <baldaquin.config.ConfigurationBase>`
abstract class. These are :

* :class:`ParameterCheckBox <baldaquin.gui.ParameterCheckBox>`,
  mapping to ``bool`` parameters;
* :class:`ParameterSpinBox <baldaquin.gui.ParameterSpinBox>`,
  mapping to ``int`` parameters;
* :class:`ParameterDoubleSpinBox <baldaquin.gui.ParameterDoubleSpinBox>`,
  mapping to ``float`` parameters;
* :class:`ParameterLineEdit <baldaquin.gui.ParameterLineEdit>`,
  mapping to ``str`` parameters with no ``choices`` constraints;
* :class:`ParameterComboBox <baldaquin.gui.ParameterComboBox>`,
  mapping to ``str`` parameters with ``choices`` constraints;


Module documentation
--------------------

.. automodule:: baldaquin.gui
