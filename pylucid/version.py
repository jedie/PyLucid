"""
    PyLucid
    ~~~~~~~

    :copyleft: 2009-2018 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# https://pypi.org/project/PyLucid/#history

__version__ = "3.0.0.dev16"
# Note:
#
# If pre-release should be publish to PyPi:
#   * Set pip '--pre' flag in pylucid_boot.NORMAL_INSTALL
#   * push not pre-releases on 'master' branch
#


# Just the first two parts of the version
# This added to template context to display the PyLucid Verion on the page.
safe_version = ".".join(__version__.split(".")[:2])
