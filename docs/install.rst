.. _install:

Installation
============

In a nutshell,

.. code-block:: shell

    pip install baldaquin

This should get you up and running. (Of course all the usual suggestions about using
a virtual environment apply here, see the `venv <https://docs.python.org/3/library/venv.html>`_
documentation page.)

Once you have installed the package, you should be able to type

.. code-block:: shell

    baldaquin start-app silly_hist

and see a GUI appear. Press play and enjoy the histogram filling itself.


Pre-requisites
--------------

If you pip-install the package, all the dependencies should get installed auto-magically.
That said, here are a few words about what ``baldaquin`` needs under the hood in
order to be able to run, just in case you need to debug any problem.

The ``pyproject.toml`` file is the ultimate reference in terms of what you need
to run ``plasduino``---here is the relevant excerpt.

.. literalinclude:: ../pyproject.toml
    :language: toml
    :start-at: [project]
    :end-at: requires-python


Python
~~~~~~

Note we try and support all Python versions from 3.7 on.
`This page <https://nedbatchelder.com/text/which-py.html?ref=nicholashairs.com>`_
includes a succinct summary of the new features in each Python version, and is a
useful resource. Python 3.6 brought about f-strings, and we do use them all over
the place; Python 3.7 includes postponed evaluation of type annotations and dataclasses,
which we also use extensively. (In addition, the dict order is guaranteed from
Python 3.7 on, which is handy.)

`Python 3.7 was released on June 27, 2018, and its EOL was in June 2023---well before
this project started. If you are running an older Python version you should
definitely conside upgrading.`

By the way: if you are tinkering with the Python installation, you should
definitely take a look at `pyenv <https://github.com/pyenv/pyenv>`_. You'll love it.


Python packages
~~~~~~~~~~~~~~~

Here is a list of quick pointers to the various packages you need, and why is that:

* `loguru <https://github.com/Delgan/loguru>`_: a logging package that is far better
  than the one provided by the Python standard library;
* `matplotlib <https://matplotlib.org/>`_: the standard Python plotting package;
* `numpy <https://numpy.org/>`_: the fundamental Python numerical module;
* `pydata-sphinx-theme <https://pydata-sphinx-theme.readthedocs.io/en/stable/>`_:
  the sphinx theme used for this documentation;
* `pyserial <https://github.com/pyserial/pyserial>`_: a Python library for interacting
  with the serial port;
* `PySide6 <https://doc.qt.io/qtforpython-6/>`_: the official Python wrappers over the
  Qt GUI toolkit;
* `scipy <https://scipy.org/>`_: Python package providing advanced numerical algorithms.


Other stuff
~~~~~~~~~~~

Depending on what exactly you want to achieve with ``baldaquin`` there might be
other things that you need to install. (We shall try and point that out in the
relevant parts of the documentation when that is the case). This might include:

* `arduino-cli <https://github.com/arduino/arduino-cli>`_: the Arduino command-line
  tool;
* `avrdude <https://github.com/avrdudes/avrdude>`_: an utility to program
  micro-controllers.