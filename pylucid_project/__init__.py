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

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

try:
    from django.utils.version import get_svn_revision
except ImportError:
    svn_revision = ""
else:
    svn_revision = get_svn_revision(".")
    if svn_revision == u'SVN-unknown':
        svn_revision = ""
    else:
        # Add a space between the normal version number
        # and the SVN revision number.
        svn_revision = " (%s)" % svn_revision

__version__ = (0, 9, 0, 'pre-alpha', svn_revision)

# PyLucid Version String
# Important for setuptools:
# - Only use . as a separator
# - No spaces: "0.8.0 RC2" -> "0.8.0RC2"
# http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
PYLUCID_VERSION_STRING = "%s.%s.%s%s%s" % __version__