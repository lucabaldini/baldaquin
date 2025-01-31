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

Three different setup scripts are provided in order to facilitate code
development---all of them essentially prepends the package root folder to the
``$PYTHONPATH`` environmental variable to that you will be able to import the
Python modules as if the package was pip-installed.

GNU/Linux
~~~~~~~~~

Assuming that your uses a bash-like syntax, all you have to do is

.. code-block:: shell

    [lbaldini@pcpi0188 baldaquin]$ source setup.sh
    BALDAQUIN_ROOT -> /home/users/lbaldini/work/baldaquin
    PYTHONPATH -> /home/users/lbaldini/work/baldaquin:

from within the root folder of the package.


Windows
~~~~~~~

For windows we provide setup scripts for both the old-good command prompt and
for the Windows power shell. In the first case the thing is fairly similar to
GNU/Linux:

.. code-block:: shell

    C:\work\baldaquin>.\setup.bat
    BALDAQUIN_ROOT -> C:\work\baldaquin
    Updated PYTHONPATH -> C:\work\baldaquin;

If you are using the power shell, instead, things might be a little bit more
complicated, as it is likely that system is configured to not allow you to run
a script unless you specifically ask to do so, and you will need an extra command

.. code-block:: shell

    PS C:\work\baldaquin> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    PS C:\work\baldaquin> . .\setup.ps1
    BALDAQUIN_ROOT -> C:\work\baldaquin
    Updated PYTHONPATH -> C:\work\baldaquin;

Two things worth noticing:

* dot-sourcing the script (i.e., ``. .\setup.ps1``) is a real thing---if you don't
  add the extra dot-space at the beginning of the line, the new environmental
  variable will only live within the scope of the script, and will not be propagated
  to the parent shell;
* the ``Set-ExecutionPolicy`` command is the one that let you temporarily execute
  scripts.


Static analysis
---------------

Static code analyzers help maintaining the codebase consistent and readable, and
potentially help catching mistakes and shortcomings.

The top-level `Makefile` includes specific targets for code analysis/linting, and
you should always run it before committing code

.. code-block:: shell

    [lbaldini@pcpi0188 baldaquin]$ make
    ruff check .
    All checks passed!
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
    0
    pylint baldaquin \
        --disable too-many-ancestors \
        --disable too-many-arguments \
        --disable too-many-function-args \
        --disable too-many-instance-attributes \
        --disable c-extension-no-member \
        --disable use-dict-literal \
        --disable too-many-positional-arguments \
        --disable too-many-public-methods \
        --ignore _version.py

    --------------------------------------------------------------------
    Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)


Note that linting is included in our continuous integration, so your pull requests
will just fail the tests if you don't :-)



Compiling the documentation
---------------------------

The documentation is automatically compiled on github pages whenever a pull request
is merged on the main branch.

You can compile the documentation locally by just typing

.. code-block:: shell

    [lbaldini@pcpi0188 baldaquin]$ make html



Creating a release
------------------

We have a small tool helping with the release process

.. code-block:: shell

    [lbaldini@pcpi0188 baldaquin]$ python tools/release.py --help
    usage: release.py [-h] {major,minor,patch}

    positional arguments:
    {major,minor,patch}  Tag increment mode

    options:
    -h, --help           show this help message and exit

At this time this is pretty rudimentary, and what it does is simply incrementing
a given field of the version identifier, updating the relevant files, pushing to
git and creating a tag.

Uploading a release on PyPi is done manually from the github page.