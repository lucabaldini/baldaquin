.. _install:

Installation
============

In a nutshell,

.. code-block:: shell

    pip install baldaquin

This should get you up and running. (Of course all the usual suggestions about using
a virtual environment apply here, see the `venv <https://docs.python.org/3/library/venv.html>`_
documentation page.)


Pre-requisites
--------------

The ``pyproject.toml`` file is the ultimate reference in terms of what you need
to run ``plasduino``---here is the relevant excerpt.

.. literalinclude:: ../pyproject.toml
    :language: toml
    :start-at: [project]
    :end-at: requires-python
