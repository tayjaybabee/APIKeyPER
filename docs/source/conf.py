import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "APIKeyPER"
author = "Taylor"

# The full version, including alpha/beta/rc tags
release = "1.0-dev1"

# Add any Sphinx extension module names here, as strings.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.autoprogram",
    "recommonmark",
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

# If true, "Created using Sphinx" is shown in the HTML footer.
html_show_sphinx = False

# If true, "todo" and "todoList" produce output, else they produce nothing.
todo_include_todos = True

# Intersphinx mapping (might require configuration based on the libraries you use)
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
