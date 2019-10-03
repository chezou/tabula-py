# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import inspect
import os
import subprocess
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sphinx_rtd_theme

GH_ORGANIZATION = "chezou"
GH_PROJECT = "tabula-py"
MODULE = "tabula"


def linkcode_resolve(domain, info):
    """Generate link to GitHub.
    References:
    - https://github.com/scikit-learn/scikit-learn/blob/f0faaee45762d0a5c75dcf3d487c118b10e1a5a8/doc/conf.py
    - https://github.com/chainer/chainer/pull/2758/
    """
    if domain != "py" or not info["module"]:
        return None

    # tag
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    except (subprocess.CalledProcessError, OSError):
        print("Failed to execute git to get revision")
        return None
    revision = revision.decode("utf-8")

    obj = sys.modules.get(info["module"])
    if obj is None:
        return None
    for comp in info["fullname"].split("."):
        obj = getattr(obj, comp)

    # filename
    try:
        filename = inspect.getsourcefile(obj)
    except Exception:
        return None
    if filename is None:
        return None

    # relpath
    pkg_root_dir = os.path.dirname(__import__(MODULE).__file__)
    filename = os.path.realpath(filename)
    if not filename.startswith(pkg_root_dir):
        return None
    relpath = os.path.relpath(filename, pkg_root_dir)

    # line number
    try:
        linenum = inspect.getsourcelines(obj)[1]
    except Exception:
        linenum = ""

    return "https://github.com/{}/{}/blob/{}/{}/{}#L{}".format(
        GH_ORGANIZATION, GH_PROJECT, revision, MODULE, relpath, linenum
    )

# -- Project information -----------------------------------------------------

project = 'tabula-py'
copyright = '2019, Aki Ariga'
author = 'Aki Ariga'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx.ext.linkcode",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Work around for contents.rst not found error
# See also: https://github.com/readthedocs/readthedocs.org/issues/2569
master_doc = 'index'
