# coding: utf-8

"""
    PyLucid version info
    ~~~~~~~~~~~~~~~~~~~~


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


try:
    from django.utils.version import get_svn_revision

    svn_revision = get_svn_revision("PyLucid")
    if svn_revision == u'SVN-unknown':
        # No SVN checkout, a release?
        svn_revision = ""
    else:
        # Add a space between the normal version number
        # and the SVN revision number.
        svn_revision = " " + svn_revision
except ImportError:
    # using /setup.py in the lite version without django in the sys.path
    svn_revision = ""

__version__ = (0, 9, 0, 'pre-alpha', svn_revision)