'''
Re-runs the given command every time files are modified in the current
directory or its subdirectories.
'''
from .version import __version__

# __doc__ and __version__ from here are seen by pydoc, read by setup.py,
# and generate output for --help.

import warnings

warning_message = (
    "\n\tThe rerun file change detector is deprecated and will be removed from pypi."
    "\n\tPlease install directly from https://github.com/tartley/rerun and pin to < 1.0.31 if you want to continue using it."
    "\n\tIf you are looking for the Rerun robotics library, please install the rerun-sdk package from pypi instead."
)

warnings.warn(warning_message)
