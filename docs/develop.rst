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

We have a small tool helping with the release process

.. code-block:: shell

    lbaldini@nblbaldini:~/work/baldaquin$ python tools/release.py --help
    usage: release.py [-h] {major,minor,micro}

    Release a new version of the package.

    positional arguments:
    {major,minor,micro}  The version bump mode.

    options:
    -h, --help           show this help message and exit

At this time this is pretty rudimentary, and what it does is simply incrementing
a given field of the version identifier, updating the relevant files, pushing to
git and creating a tag.