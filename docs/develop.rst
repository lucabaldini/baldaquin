.. _develop:

Development
===========

Here is a few semi-random notes about the baldaquin development, which might be
useful for advanced users and people willing to contribute to the package.

For reference, `here <https://www.stuartellis.name/articles/python-modern-practices/>`_
is a good resource, and one that we have borrowed from a lot---happy reading.


Python installation
-------------------

Making sure that a given piece of code works across different Python version is
not completely trivial. (At the time of writing, e.g., we test against Python 3.7
and 3.13 in our continuos integration, but from time to time it is handy to be
able to switch between Python versions locally, too.)

`pyenv <https://github.com/pyenv/pyenv>`_ is a `beautiful` version management system
that lets you just do that. (The github README covers the installation and setup.)
The basic idea is that, once you have pyenv up and running, you can install multiple
version of Python, e.g.

.. code-block:: shell

    pyenv install 3.7
    pyenv install 3.13

and then seamlessly switch between them

.. code-block:: shell

    pyenv shell 3.13



Environment
-----------


Development
-----------

Creating a release
------------------

The package includes a simple release script, located in the ``tools/`` directory,
which automates the version bump, changelog update, git tagging, and publishing
to PyPI. To use it, simply run:

.. program-output:: python ../tools/release.py --help
