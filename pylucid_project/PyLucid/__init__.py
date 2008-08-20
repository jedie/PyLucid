"""
    PyLucid
    ~~~~~~~

    A Python based Content Management System
    written with the help of the powerful
    Webframework Django.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

try:
    from django.utils.version import get_svn_revision

    svn_revision = get_svn_revision("PyLucid")
    if svn_revision == u'SVN-unknown':
        # No SVN checkout, a release?
        svn_revision = ""
    else:
        # Add a space between the normal version number and the SVN revision number.
        svn_revision = " " + svn_revision
except ImportError:
    # using /setup.py in the lite version without django in the sys.path
    svn_revision = ""

# PyLucid Version String
# Important for setuptools:
# - Only use . as a separator
# - No spaces: "0.8.0 RC2" -> "0.8.0RC2"
# http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
PYLUCID_VERSION = (0, 8, 5, svn_revision)
PYLUCID_VERSION_STRING = "0.8.5RC1" + svn_revision


#______________________________________________________________________________
# LOW-LEVEL WARNING REDIRECT
"""
This part is commented out per default. Use only for debugging!
It's for "handle egg warning...":http://pylucid.net:8080/pylucid/ticket/195
"""
import warnings, logging

# Needs to have the file rights to create/write into this file!
LOGFILE = "PyLucid_warnings.log"

try:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        filename=LOGFILE,
        filemode='a'
    )
except IOError, err:
    raise IOError("Can't setup low level warning redirect: %s" % err)

log = logging.debug
log("PyLucid warnings logging started.")

warning_container = []

def showwarning(message, category, filename, lineno):

    msg = unicode(message)
    filename = u"..." + filename[-30:]
    msg += u" (%s - line %s)" % (filename, lineno)

    log(msg)

old_showwarning = warnings.showwarning
warnings.showwarning = showwarning
