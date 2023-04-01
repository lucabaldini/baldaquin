.. _gui:

:mod:`baldaquin.gui` --- Basic GUI elements
===========================================

This module provides all the basic building blocks for the advanced GUI
widgets.


Low-level widgets
-----------------

At the lowest level, the module provides a number of classes that act as lightweight
wrappers over standard Qt widget, with the twofold purpose of enforcing consistency
in the overall look and feel of the interface and minimizing boilerplate code:

* :class:`Button <baldaquin.gui.Button>` represents a simple button equipped with
  an icon, and is used in the :class:`ControlBar <baldaquin.gui.ControlBar>`;


The control bar
---------------


Displaying data
---------------

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
