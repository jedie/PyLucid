# coding: utf-8
"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.

    :copyleft: 2009-2015 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

__version__ = (2,0,0,"beta")


VERSION_STRING = '.'.join(str(part) for part in __version__)


if __name__ == "__main__":
    print(VERSION_STRING)
