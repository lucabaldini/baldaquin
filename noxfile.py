# Copyright (C) 2025 the baldaquin team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pathlib
import shutil

import nox

__package_name__ = "baldaquin"

# Basic environment.
_ROOT_DIR = pathlib.Path(__file__).parent
_DOCS_DIR = _ROOT_DIR / "docs"
_SRC_DIR = _ROOT_DIR / "src" / __package_name__
_TESTS_DIR = _ROOT_DIR / "tests"

# Folders containing source code that potentially needs linting.
_LINT_DIRS = ("src", "tests", "tools")

# Reuse existing virtualenvs by default.
nox.options.reuse_existing_virtualenvs = True


@nox.session(venv_backend="none")
def cleanup(session: nox.Session) -> None:
    """Cleanup temporary files.
    """
    # Remove Python cache and build artifacts.
    session.log("Cleaning up __pycache__ and build artifacts...")
    patterns = ("__pycache__", "*.pyc", "*.pyo", "*.pyd")
    _path = _ROOT_DIR / "__pycache__"
    if _path.is_dir():
        session.log(f"Removing folder {_path}...")
        shutil.rmtree(_path)
    for pattern in patterns:
        for folder_path in (_SRC_DIR, _TESTS_DIR):
            for _path in folder_path.rglob(pattern):
                if _path.is_dir():
                    session.log(f"Removing folder {_path}...")
                    shutil.rmtree(_path)
                elif _path.is_file():
                    session.log(f"Removing file {_path}...")
                    _path.unlink()
    # Cleanup the docs.
    session.log("Cleaning up docs...")
    for folder_name in ("_build", "auto_examples"):
        _path = _DOCS_DIR / folder_name
        if _path.exists():
            session.log(f"Removing folder {_path}...")
            shutil.rmtree(_path)


@nox.session(venv_backend="none")
def docs(session: nox.Session) -> None:
    """Build the HTML docs.

    Note this is a nox session with no virtual environment, based on the assumption
    that it is not very interesting to build the documentation with different
    versions of Python or the associated environment, since the final thing will
    be created remotely anyway. (This also illustrates the use of the nox.session
    decorator called with arguments.)
    """
    source_dir = _DOCS_DIR
    output_dir = _DOCS_DIR / "_build" / "html"
    session.run("sphinx-build", "-b", "html", source_dir, output_dir, *session.posargs)


@nox.session
def ruff(session: nox.Session) -> None:
    """Run ruff.
    """
    session.install("ruff")
    session.install(".[dev]")
    session.run("ruff", "check", *session.posargs)


@nox.session
def pylint(session: nox.Session) -> None:
    """Run pylint.
    """
    session.install("pylint")
    session.install(".[dev]")
    session.run("pylint", *_LINT_DIRS, *session.posargs)


@nox.session
def test(session: nox.Session) -> None:
    """Run the unit tests.
    """
    session.install("pytest")
    session.install(".[dev]")
    session.run("pytest", *session.posargs)