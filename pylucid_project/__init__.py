# coding: utf-8
"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

__version__ = (0, 9, 0, 'RC2')

try:
    from django.utils.version import get_svn_revision
except ImportError:
    pass
else:
    path = os.path.split(os.path.abspath(__file__))[0]
    svn_revision = get_svn_revision(path)
    if svn_revision != u'SVN-unknown':
        svn_revision = svn_revision.replace("-", "").lower()
        __version__ += (svn_revision,)


VERSION_STRING = '.'.join(str(part) for part in __version__)


if __name__ == "__main__":
    print VERSION_STRING
