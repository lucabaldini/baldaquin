# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import importlib.metadata

from baldaquin import __version__, __name__ as __package_name__


# Get package metadata.
_metadata = importlib.metadata.metadata(__package_name__)


# --- Project information ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = __package_name__
author = _metadata["Author-email"]
copyright = f"2025-%Y, {author}"
version = __version__
release = version

# --- General configuration ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.imgmath",
    "sphinx.ext.extlinks",
    "sphinxcontrib.programoutput",
]
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "private-members": True
}
todo_include_todos = True

# Options for syntax highlighting.
pygments_style = "default"
pygments_dark_style = "default"

# Options for internationalization.
language = "en"

# Options for markup.
rst_prolog = f"""
"""

# Options for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Options for templating.
templates_path = ["_templates"]


# --- Options for HTML output ---
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_theme_options = {
    "awesome_external_links": True,
}
#html_logo = "_static/baldaquin_logo_small_light.png"
#html_favicon = "_static/favicon.ico"
html_permalinks_icon = "<span>#</span>"
html_static_path = ["_static"]

